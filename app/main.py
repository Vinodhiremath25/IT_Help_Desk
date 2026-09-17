from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from app.agent.graph import agent_app, SENSITIVE_TOOLS
from app.agent.tools import MOCK_TICKETS_DB

app = FastAPI(title="AutoDesk AI API", version="1.0.0")

class ChatRequest(BaseModel):
    user_id: str
    message: str
    thread_id: Optional[str] = "default-thread"

class ApprovalRequest(BaseModel):
    thread_id: str
    approved: bool

class ChatResponse(BaseModel):
    reply: str
    actions_taken: List[str]
    pending_approval: Optional[Dict[str, Any]] = None

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def serve_ui():
    return FileResponse("app/static/index.html")

@app.get("/health")
def health_check():
    return {"status": "healthy", "provider": "groq", "model": "llama-3.3-70b-versatile"}

@app.get("/api/tickets")
def get_tickets():
    return {"tickets": list(MOCK_TICKETS_DB.values())}

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest):
    try:
        prompt = f"Employee {payload.user_id}: {payload.message}"
        input_data = {
            "messages": [HumanMessage(content=prompt)],
            "user_id": payload.user_id,
        }
        config = {"configurable": {"thread_id": payload.thread_id}}

        # Run until completion or interrupt
        result = agent_app.invoke(input_data, config=config)
        state = agent_app.get_state(config)

        # Check if execution paused before the tools node
        if state.next and "tools" in state.next:
            last_message = state.values["messages"][-1]
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                call = last_message.tool_calls[0]
                
                # Check for sensitive actions requiring human approval
                if call["name"] in SENSITIVE_TOOLS:
                    return ChatResponse(
                        reply=f"Action requires administrator authorization: Requesting approval to run '{call['name']}' for {call['args']}.",
                        actions_taken=[f"Awaiting approval: {call['name']}"],
                        pending_approval={
                            "tool_name": call["name"],
                            "tool_args": call["args"],
                            "thread_id": payload.thread_id
                        }
                    )
                else:
                    # Automatically resume safe tools (RAG search, ticket creation, etc.)
                    result = agent_app.invoke(None, config=config)

        actions = []
        final_reply = "Request processed."
        for msg in result["messages"]:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    actions.append(f"{tc['name']}({tc['args']})")
            elif isinstance(msg, AIMessage) and msg.content:
                final_reply = msg.content

        return ChatResponse(reply=final_reply, actions_taken=actions, pending_approval=None)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/approve", response_model=ChatResponse)
def approve_action(payload: ApprovalRequest):
    try:
        config = {"configurable": {"thread_id": payload.thread_id}}
        state = agent_app.get_state(config)

        if not state.next or "tools" not in state.next:
            raise HTTPException(status_code=400, detail="No action is currently awaiting approval.")

        last_message = state.values["messages"][-1]
        call = last_message.tool_calls[0]

        if payload.approved:
            # Resume graph execution
            result = agent_app.invoke(None, config=config)
            actions = [f"Approved & Executed: {call['name']}"]
            final_reply = "Action approved and completed successfully."

            for msg in result["messages"]:
                if isinstance(msg, AIMessage) and msg.content:
                    final_reply = msg.content

            return ChatResponse(reply=final_reply, actions_taken=actions, pending_approval=None)
        else:
            # Inject rejection message into state
            rejection_message = ToolMessage(
                tool_call_id=call["id"],
                content="Action rejected by system administrator."
            )
            agent_app.update_state(config, {"messages": [rejection_message]}, as_node="tools")
            result = agent_app.invoke(None, config=config)

            return ChatResponse(
                reply="The requested action was rejected by the administrator.",
                actions_taken=[f"Rejected: {call['name']}"],
                pending_approval=None
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
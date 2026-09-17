import os
from typing import Literal
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from app.agent.state import AgentState
from app.agent.tools import (
    check_mfa_status,
    reset_mfa_token,
    create_jira_ticket,
    search_knowledge_base,
)

# 1. Register tools
tools = [check_mfa_status, reset_mfa_token, create_jira_ticket, search_knowledge_base]
tool_node = ToolNode(tools)

# Sensitive operations that require human approval
SENSITIVE_TOOLS = {"reset_mfa_token"}

# 2. Cloud Groq Llama 3.3 Engine
print(">>> INITIALIZING GROQ CLOUD ENGINE (llama-3.3-70b-versatile)...")
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
).bind_tools(tools)

# 3. System Instructions
SYSTEM_PROMPT = """You are AutoDesk AI, an autonomous internal IT helpdesk assistant.
Your job is to assist employees with IT issues, check account statuses, search internal documentation, and reset credentials.

Key Rules:
- When employees ask general troubleshooting questions (e.g. VPN issues, Wi-Fi connectivity, software approval, hardware policy), invoke `search_knowledge_base` first to retrieve corporate policy.
- When invoking tools like `check_mfa_status` or `reset_mfa_token`, pass the employee's ID (e.g. EMP101).
- If an issue cannot be resolved through documentation or automated tools, create an escalation ticket using `create_jira_ticket`.
- Once a tool completes, clearly summarize the result for the user.
"""

def assistant_node(state: AgentState):
    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
        
    response = llm.invoke(messages)
    return {"messages": [response]}

def route_tools_or_end(state: AgentState) -> Literal["tools", "__end__"]:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

# 4. State Machine Workflow
workflow = StateGraph(AgentState)

workflow.add_node("assistant", assistant_node)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "assistant")
workflow.add_conditional_edges(
    "assistant",
    route_tools_or_end,
    {"tools": "tools", END: END}
)
workflow.add_edge("tools", "assistant")

checkpointer = MemorySaver()

# Intercept sensitive actions before tool execution
agent_app = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["tools"]
)
from langchain_core.messages import HumanMessage
from app.agent.graph import agent_app

def run_test():
    print("Testing AutoDesk AI Agent with local Llama 3.2...\n")
    
    # Test Case: Employee EMP101 asks about locked MFA
    test_input = {
        "messages": [
            HumanMessage(content="Hi, my employee ID is EMP101. My Okta MFA seems locked out, can you check it?")
        ],
        "user_id": "EMP101",
        "department": "Engineering",
        "current_category": "IAM",
        "extracted_params": {},
        "requires_escalation": False,
        "requires_human_approval": False,
        "ticket_id": None
    }

    # Run graph
    result = agent_app.invoke(test_input)

    print("--- Graph Execution Completed ---")
    for msg in result["messages"]:
        role = msg.__class__.__name__
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"\n[{role} -> Tool Call]: {msg.tool_calls}")
        else:
            print(f"\n[{role}]: {msg.content}")

if __name__ == "__main__":
    run_test()
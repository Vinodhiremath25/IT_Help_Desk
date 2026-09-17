import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from langchain_core.tools import tool

# In-memory mock databases
MOCK_TICKETS_DB: Dict[str, Dict[str, Any]] = {}
MOCK_OKTA_USERS: Dict[str, Dict[str, Any]] = {
    "EMP101": {"name": "Alice Smith", "mfa_status": "locked", "email": "alice@company.com"},
    "EMP102": {"name": "Bob Jones", "mfa_status": "active", "email": "bob@company.com"}
}

@tool
def check_mfa_status(user_id: Optional[str] = None) -> Dict[str, Any]:
    """Inspects an employee's multi-factor authentication (MFA) status.
    
    Args:
        user_id: The employee ID string, for example 'EMP101'.
    """
    clean_id = (user_id or "").strip().upper()
    
    # Automatic fallback if small model passes empty string, 'NONE', or generic pronouns
    if not clean_id or clean_id in ["NONE", "ME", "USER", "DEFAULT"]:
        clean_id = "EMP101"

    user = MOCK_OKTA_USERS.get(clean_id)
    if not user:
        return {
            "status": "error",
            "message": f"User ID '{clean_id}' was not found. Valid IDs: EMP101, EMP102."
        }
        
    return {
        "status": "success",
        "user_id": clean_id,
        "name": user["name"],
        "mfa_status": user["mfa_status"]
    }

@tool
def reset_mfa_token(user_id: Optional[str] = None) -> Dict[str, Any]:
    """Resets a locked MFA token and triggers an activation email.
    
    Args:
        user_id: The employee ID string, for example 'EMP101'.
    """
    clean_id = (user_id or "").strip().upper()
    if not clean_id or clean_id in ["NONE", "ME", "USER", "DEFAULT"]:
        clean_id = "EMP101"

    user = MOCK_OKTA_USERS.get(clean_id)
    if not user:
        return {"status": "error", "message": f"User ID '{clean_id}' was not found."}
        
    user["mfa_status"] = "active"
    return {
        "status": "success",
        "message": f"MFA token reset completed. An activation link has been sent to {user['email']}."
    }

@tool
def create_jira_ticket(
    user_id: str,
    category: str,
    title: str,
    description: str,
    priority: str = "medium"
) -> Dict[str, Any]:
    """Generates an IT escalation ticket in Jira for hardware or unresolved incidents."""
    ticket_id = f"IT-{uuid.uuid4().hex[:5].upper()}"
    record = {
        "ticket_id": ticket_id,
        "user_id": user_id,
        "category": category,
        "title": title,
        "description": description,
        "priority": priority,
        "status": "OPEN",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    MOCK_TICKETS_DB[ticket_id] = record
    return {
        "status": "success",
        "ticket_id": ticket_id,
        "message": f"Ticket {ticket_id} created successfully."
    }

from app.agent.rag import query_knowledge_base

@tool
def search_knowledge_base(query: str) -> Dict[str, Any]:
    """Searches official IT documentation, policies, VPN troubleshooting, Wi-Fi configuration, and approved software lists.
    
    Args:
        query: Specific search terms or question regarding corporate IT policies or troubleshooting steps.
    """
    results = query_knowledge_base(query)
    return {
        "status": "success",
        "results": results
    }
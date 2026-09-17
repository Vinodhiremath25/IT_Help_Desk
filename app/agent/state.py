from typing import Annotated, Sequence, TypedDict, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # 'add_messages' ensures conversation history appends rather than overwriting
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_id: str
    department: Optional[str]
    current_category: Optional[str]
    extracted_params: dict
    requires_escalation: bool
    requires_human_approval: bool
    ticket_id: Optional[str]
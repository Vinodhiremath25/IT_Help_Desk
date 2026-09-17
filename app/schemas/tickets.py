from enum import Enum
from pydantic import BaseModel
from typing import Optional

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TicketCategory(str, Enum):
    IAM = "IAM"
    NETWORK = "Network"
    HARDWARE = "Hardware"
    SOFTWARE = "Software"

class TicketCreate(BaseModel):
    user_id: str
    category: TicketCategory
    title: str
    description: str
    priority: TicketPriority = TicketPriority.MEDIUM
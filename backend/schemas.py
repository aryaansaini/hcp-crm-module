from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime

class HCPCreate(BaseModel):
    name: str
    specialty: Optional[str] = None
    hospital: Optional[str] = None

class HCPResponse(HCPCreate):
    id: int
    class Config:
        from_attributes = True

class InteractionCreate(BaseModel):
    hcp_id: int
    interaction_type: Optional[str] = "Meeting"
    interaction_date: Optional[date] = None
    interaction_time: Optional[time] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    sentiment: Optional[str] = "Neutral"
    outcomes: Optional[str] = None
    followup_actions: Optional[str] = None

class InteractionUpdate(BaseModel):
    # Edit ke time sab fields optional honge — sirf jo change karna hai wahi bhejo
    interaction_type: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    followup_actions: Optional[str] = None

class InteractionResponse(InteractionCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
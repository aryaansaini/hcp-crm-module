from sqlalchemy import Column, Integer, String, Text, Date, Time, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from database import Base

class HCP(Base):
    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    specialty = Column(String(255))
    hospital = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"))
    interaction_type = Column(String(50), default="Meeting")
    interaction_date = Column(Date)
    interaction_time = Column(Time)
    attendees = Column(Text)
    topics_discussed = Column(Text)
    materials_shared = Column(Text)
    samples_distributed = Column(Text)
    sentiment = Column(Enum("Positive", "Neutral", "Negative"), default="Neutral")
    outcomes = Column(Text)
    followup_actions = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from agent import run_agent
from pydantic import BaseModel

import models, schemas
from database import engine, get_db

# Tables auto-create ho jayengi agar already nahi hain (models.py ke basis pe)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="HCP CRM - AI Log Interaction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "HCP CRM Backend is running"}

# ---------- HCP Endpoints ----------

@app.post("/hcps", response_model=schemas.HCPResponse)
def create_hcp(hcp: schemas.HCPCreate, db: Session = Depends(get_db)):
    db_hcp = models.HCP(**hcp.dict())
    db.add(db_hcp)
    db.commit()
    db.refresh(db_hcp)
    return db_hcp

@app.get("/hcps", response_model=list[schemas.HCPResponse])
def list_hcps(db: Session = Depends(get_db)):
    return db.query(models.HCP).all()

# ---------- Interaction Endpoints ----------

@app.post("/interactions", response_model=schemas.InteractionResponse)
def create_interaction(interaction: schemas.InteractionCreate, db: Session = Depends(get_db)):
    db_interaction = models.Interaction(**interaction.dict())
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction

@app.get("/interactions", response_model=list[schemas.InteractionResponse])
def list_interactions(db: Session = Depends(get_db)):
    return db.query(models.Interaction).all()

@app.put("/interactions/{interaction_id}", response_model=schemas.InteractionResponse)
def update_interaction(interaction_id: int, update: schemas.InteractionUpdate, db: Session = Depends(get_db)):
    db_interaction = db.query(models.Interaction).filter(models.Interaction.id == interaction_id).first()
    if not db_interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    for field, value in update.dict(exclude_unset=True).items():
        setattr(db_interaction, field, value)

    db.commit()
    db.refresh(db_interaction)
    return db_interaction

# ---------- Chat / AI Agent Endpoint ----------

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat_with_agent(request: ChatRequest, db: Session = Depends(get_db)):
    response = run_agent(db, request.message)
    return {"response": response}
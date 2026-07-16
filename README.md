


# AI-First CRM – HCP Log Interaction Module

An AI-first Customer Relationship Management (CRM) module built for pharmaceutical 
field representatives to log their interactions with Healthcare Professionals (HCPs). 
The screen supports two ways of logging an interaction: a traditional structured form, 
and a conversational AI chat interface powered by a LangGraph agent backed by a Groq-hosted LLM.

---

## Table of Contents
- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [LangGraph Agent & Tools](#langgraph-agent--tools)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [How to Use](#how-to-use)
- [Known Limitations / Future Improvements](#known-limitations--future-improvements)

---

## Overview

Field reps need a fast way to record what happened during a doctor visit — who they 
met, what was discussed, the doctor's sentiment, and next steps. This module offers:

1. **Structured Form** — a traditional form (HCP name, date/time, attendees, topics, 
   sentiment, outcomes, follow-ups) for precise, manual entry.
2. **AI Chat Panel** — the rep can just type a natural sentence like *"Met Dr. Sharma, 
   discussed new cardiac drug, positive response, shared brochure"* and the LangGraph 
   agent extracts the relevant fields, decides which action to take, and persists it 
   to the database — no manual form-filling required.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Redux Toolkit, Axios |
| Backend | Python 3.10, FastAPI, Uvicorn |
| AI Agent Framework | LangGraph (prebuilt ReAct agent) |
| LLM Provider | Groq — `openai/gpt-oss-20b` |
| ORM / DB Driver | SQLAlchemy + PyMySQL |
| Database | MySQL 8.0 |
| Styling | Custom CSS (Inter font) |

> **Note on LLM model:** The original task spec asked for Groq's `gemma2-9b-it` model. 
> That model has since been **decommissioned by Groq**. This project uses 
> `openai/gpt-oss-20b`, Groq's currently recommended production model with strong 
> tool-calling support, as a drop-in replacement.

---

## Architecture

```
┌─────────────┐      HTTP (Axios)      ┌──────────────┐
│   React UI  │ ─────────────────────▶ │   FastAPI    │
│ (Form+Chat) │ ◀───────────────────── │   Backend    │
└─────────────┘                         └──────┬───────┘
                                                │
                          ┌─────────────────────┼─────────────────────┐
                          │                     │                     │
                   /interactions          /chat (LangGraph)      /hcps
                   (direct CRUD)                │
                                          ┌──────▼───────┐
                                          │ LangGraph     │
                                          │ ReAct Agent   │
                                          │ (Groq LLM)    │
                                          └──────┬───────┘
                                                 │ picks & runs a tool
                                   ┌─────────────┼─────────────┬──────────────┬───────────────┐
                                   ▼             ▼             ▼              ▼               ▼
                            log_interaction  edit_interaction  search_hcp_history  suggest_followup  get_sentiment_summary
                                   │             │             │              │               │
                                   └─────────────┴─────────────┴──────────────┴───────────────┘
                                                 │
                                          ┌──────▼───────┐
                                          │  MySQL DB     │
                                          │ hcps /        │
                                          │ interactions  │
                                          └───────────────┘
```

**Flow for a chat message:**
1. User types a message in the AI Assistant panel.
2. Frontend calls `POST /chat` with the message.
3. FastAPI hands the message to a LangGraph ReAct agent.
4. The agent (via the Groq LLM) reasons about intent, picks one or more of the 5 tools, 
   and calls them with extracted arguments.
5. Each tool directly reads/writes to MySQL via SQLAlchemy.
6. The agent's final natural-language response is returned to the frontend and rendered 
   as a chat bubble.

---

## LangGraph Agent & Tools

The agent is built using `langgraph.prebuilt.create_react_agent`, which wires an LLM 
and a list of tools into a ready-made reasoning loop (think → pick tool → act → 
observe → respond), so we don't need to hand-build the graph nodes/edges.

### The 5 Tools

| Tool | Purpose |
|---|---|
| **log_interaction** | Creates a new interaction. Looks up the HCP by name (creates one if it doesn't exist), then inserts a new row with topics, sentiment, outcomes, and follow-ups, using the LLM's extracted entities. |
| **edit_interaction** | Updates a single field (e.g. `outcomes`, `sentiment`) on an existing interaction by ID. |
| **search_hcp_history** | Returns all past interactions for a given HCP, formatted as a readable summary. |
| **suggest_followup** | Given a sentiment and last discussed topic, returns a recommended next action (e.g. schedule follow-up, address concerns, send material). |
| **get_sentiment_summary** | Aggregates sentiment counts (Positive/Neutral/Negative) across all interactions for an HCP. |

Each tool is defined with the `@tool` decorator from `langchain_core.tools`, and its 
docstring is what the LLM reads to decide *when* and *how* to call it — this is the 
core mechanism that lets the agent map free-text chat input to structured actions.

---

## Database Schema

```sql
CREATE TABLE hcps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    specialty VARCHAR(255),
    hospital VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE interactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hcp_id INT,
    interaction_type VARCHAR(50) DEFAULT 'Meeting',
    interaction_date DATE,
    interaction_time TIME,
    attendees TEXT,
    topics_discussed TEXT,
    materials_shared TEXT,
    samples_distributed TEXT,
    sentiment ENUM('Positive', 'Neutral', 'Negative') DEFAULT 'Neutral',
    outcomes TEXT,
    followup_actions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (hcp_id) REFERENCES hcps(id)
);
```

`hcps` is kept separate from `interactions` (normalized) since one HCP can have many 
interactions over time — this avoids duplicating doctor info on every row.

---

## Project Structure

```
hcp-crm-module/
├── backend/
│   ├── main.py            # FastAPI app & routes
│   ├── database.py        # SQLAlchemy engine/session setup
│   ├── models.py           # ORM models (HCP, Interaction)
│   ├── schemas.py          # Pydantic request/response schemas
│   ├── tools.py            # 5 LangGraph tools
│   ├── agent.py            # LangGraph ReAct agent + Groq LLM setup
│   ├── requirements.txt
│   └── .env                # DB + Groq credentials (not committed)
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   └── store.js               # Redux store
│   │   ├── features/interaction/
│   │   │   └── interactionSlice.js    # Redux slice (form state, chat, async thunks)
│   │   ├── App.js                     # Main UI (form + chat panel)
│   │   ├── App.css
│   │   └── index.js
│   └── package.json
├── .gitignore
└── README.md
```

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js & npm
- MySQL Server 8.0
- A free Groq API key from [console.groq.com](https://console.groq.com)

### 1. Database
```sql
CREATE DATABASE hcp_crm;
```
(Tables are auto-created by SQLAlchemy on backend startup — no manual table creation needed.)

### 2. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

# create a .env file (see Environment Variables section below)

uvicorn main:app --reload
```
Backend runs at `http://localhost:8000` (Swagger docs at `/docs`).

### 3. Frontend
```bash
cd frontend
npm install
npm start
```
Frontend runs at `http://localhost:3000`.

> Backend and frontend must run in **two separate terminals simultaneously**.

---

## Environment Variables

Create `backend/.env`:

```
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=hcp_crm
GROQ_API_KEY=your_groq_api_key
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/hcps` | Create a new HCP |
| GET | `/hcps` | List all HCPs |
| POST | `/interactions` | Create a new interaction (structured form) |
| GET | `/interactions` | List all interactions |
| PUT | `/interactions/{id}` | Update fields on an interaction |
| POST | `/chat` | Send a natural-language message to the LangGraph agent |

Full interactive API docs available at `http://localhost:8000/docs` (Swagger UI).

---

## How to Use

**Structured form:** Fill in HCP name, date/time, topics, sentiment, outcomes, and 
follow-ups on the left panel, then click **Log Interaction**.

**AI Chat:** Type something like:
```
Met Dr. Sharma, discussed new cardiac drug, positive response, shared brochure
```
The agent will log the interaction and suggest a follow-up. You can also ask:
```
Show me the history for Dr. Sharma
What is the sentiment summary for Dr. Sharma?
Edit interaction 4, change outcomes to "Doctor requested more clinical data"
```

---

## Known Limitations / Future Improvements

- The structured form's HCP Name field is currently free text and submits against 
  a fixed `hcp_id` for demo purposes; a production version would connect it to a 
  live `/hcps` search/autocomplete to resolve the correct HCP record.
- `materials_shared` and `samples_distributed` fields exist in the schema but aren't 
  yet exposed as UI inputs.
- The "Summarize from Voice Note" feature shown in the design mock is out of scope 
  for this prototype.
- No authentication/authorization layer — out of scope for this assignment.
```

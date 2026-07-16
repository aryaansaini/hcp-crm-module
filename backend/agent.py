import os
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from sqlalchemy.orm import Session
from tools import make_tools
from dotenv import load_dotenv

load_dotenv()

def get_agent(db: Session):
    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0
    )
    tools = make_tools(db)
    agent = create_react_agent(llm, tools)
    return agent

def run_agent(db: Session, user_message: str) -> str:
    agent = get_agent(db)
    result = agent.invoke({"messages": [("user", user_message)]})
    final_message = result["messages"][-1].content
    return final_message
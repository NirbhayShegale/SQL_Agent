import sys
import uuid
from pathlib import Path
from typing import Optional

# Ensure 'src' is in python path
src_path = Path(__file__).resolve().parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langgraph.types import Command
from Workflow.Graph import agent_app

app = FastAPI(title="Text-to-SQL Agent API", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "SQL Agent is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "agent": "online"}


class UserQuery(BaseModel):
    query: str
    thread_id: Optional[str] = None


class ResumeQuery(BaseModel):
    thread_id: str
    clarification_query: Optional[str] = None


@app.post("/query/")
def create_item(query: UserQuery):
    try:
        thread_id = query.thread_id or str(uuid.uuid4())
        
        result = agent_app.invoke(
            {"user_prompt": query.query},
            config={"configurable": {"thread_id": thread_id}}
        )

        if "__interrupt__" in result:
            return {
                "status": "awaiting_approval",
                "thread_id": thread_id,
                "review": result["__interrupt__"][0].value
            }

        sql_obj = result.get("sql_query")
        sql_query_text = sql_obj.query if hasattr(sql_obj, "query") else (str(sql_obj) if sql_obj else None)

        return {
            "status": "completed",
            "thread_id": thread_id,
            "sql_query": sql_query_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/resume/")
def resume_item(resume_data: ResumeQuery):
    try:
        thread_id = resume_data.thread_id
        clarification_query = resume_data.clarification_query
        if not clarification_query:
            raise HTTPException(status_code=400, detail="Clarification is required.")

        result = agent_app.invoke(
            Command(resume=clarification_query),
            config={"configurable": {"thread_id": thread_id}}
        )

        if "__interrupt__" in result:
            return {
                "status": "awaiting_approval",
                "thread_id": thread_id,
                "review": result["__interrupt__"][0].value
            }

        sql_obj = result.get("sql_query")
        sql_query_text = sql_obj.query if hasattr(sql_obj, "query") else (str(sql_obj) if sql_obj else None)

        return {
            "status": "completed",
            "thread_id": thread_id,
            "sql_query": sql_query_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run the FastAPI application:
# .\.venv\Scripts\uvicorn Backend.SqlAgentApi:app --reload --host 127.0.0.1 --port 8000
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


@app.post("/query/")
def create_item(query: UserQuery):
    try:
        thread_id = query.thread_id or str(uuid.uuid4())
        
        result = agent_app.invoke(
            {"user_prompt": query.query},
            config={"configurable": {"thread_id": thread_id}}
        )

        sql_obj = result.get("sql_query")
        sql_query_text = sql_obj.query if hasattr(sql_obj, "query") else (str(sql_obj) if sql_obj else None)

        clarification_obj = result.get("clarification_result")
        clarification_data = clarification_obj.model_dump() if hasattr(clarification_obj, "model_dump") else clarification_obj

        return {
            "thread_id": thread_id,
            "sql_query": sql_query_text,
            "clarification": clarification_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI application:
# uvicorn Backend.SqlAgentApi:app --reload --host 127.0.0.1 --port 8000
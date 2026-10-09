from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="QueryMind",
    description="Sql Agent API",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {"message": "QueryMind is running 🚀"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


class Query(BaseModel):
    sql: str

@app.get("/start")
async def get_user(query: Query):
    user_query = (query.sql).strip() 
    if user_query is None or user_query == "":
        raise HTTPException(
            status_code=400,
            detail="query is empty.",
        )

    return {
        "user_id": user_id,
        "name": "John",
    }



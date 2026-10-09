# Text-to-SQL Agent

An intelligent, stateful Text-to-SQL agent powered by **LangGraph**, **LangChain**, and **FastAPI** that converts natural language questions into accurate SQL queries, features schema-aware routing, clarification loops, and connects with PostgreSQL / Supabase databases.

---

## Features

- **Natural Language to SQL**: Translates user prompts into executable SQL queries tailored to your database schema.
- **Clarification Engine**: Detects ambiguous queries and prompts for clarification when necessary.
- **Graph-Based Workflow**: Built with `langgraph` for modular, maintainable, and stateful agent orchestration.
- **FastAPI REST API**: High-performance endpoint for seamless integration into web apps, dashboards, or bots.
- **Supabase / PostgreSQL Support**: Connects seamlessly with PostgreSQL databases (like Supabase).

---

## Project Structure

```text
SQL_Agent/
├── .gitignore
├── README.md
└── sqlAgent/
    ├── Backend/
    │   ├── SqlAgentApi.py       # FastAPI application endpoints
    │   └── __init__.py
    ├── src/
    │   ├── Config/              # Model and LLM configuration
    │   ├── Database/            # Database connection & schema utilities
    │   ├── Workflow/            # LangGraph state, graph definition & routing
    │   └── sqlagent/            # Agents (ClarificationEngine, QueryWriter)
    ├── .env.example             # Environment variables template
    ├── pyproject.toml           # Project dependencies & packaging config
    └── uv.lock                  # Dependency lock file
```

---

## Getting Started

### Prerequisites

- Python `>= 3.11` (or Python 3.14 via [uv](https://docs.astral.sh/uv/))
- [uv](https://docs.astral.sh/uv/) (recommended) or standard `pip`

### 1. Clone the Repository

```bash
git clone https://github.com/NirbhayShegale/SQL_Agent.git
cd SQL_Agent
```

### 2. Environment Setup

Navigate to the `sqlAgent` folder and copy `.env.example` to `.env`:

```bash
cd sqlAgent
cp .env.example .env
```

Update `.env` with your API keys and database credentials:

```env
HF_TOKEN=your_huggingface_token_here
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/dbname
```

### 3. Install Dependencies

Using `uv`:

```bash
uv sync
```

Or using `pip`:

```bash
pip install -e .
```

---

## Running the API Server

Start the FastAPI server with `uvicorn`:

```bash
uvicorn Backend.SqlAgentApi:app --reload --host 127.0.0.1 --port 8000
```

The server will be available at `http://127.0.0.1:8000`.

- **API Documentation (Swagger UI)**: `http://127.0.0.1:8000/docs`
- **Health Check**: `GET /health`
- **Query Endpoint**: `POST /chat` (also available at `POST /query/`)
- **Resume Endpoint**: `POST /resume` (also available at `POST /query/resume/`)

### Example Request

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"query": "Show me total revenue for each month in 2024"}'
```

The response includes a `thread_id`. Send that same `thread_id` with later requests to continue the conversation; earlier turns are included as context for follow-up questions. A new thread ID starts a separate conversation. Conversation history is held in memory and is cleared when the application process restarts.

Read-only SQL runs immediately. Potentially modifying SQL pauses with `"status": "confirmation_required"` and includes the SQL and a confirmation message. Resume the same thread with the user's free-text response:

```bash
curl -X POST "http://127.0.0.1:8000/resume" \
     -H "Content-Type: application/json" \
     -d '{"thread_id": "<thread_id>", "user_response": "yes, go ahead"}'
```

Only a clearly affirmative response proceeds to execution. Any other response cancels the query without executing SQL. Ambiguous questions can also pause for clarification; send their answer to the same resume endpoint and thread ID.

---

## Tech Stack

- **Frameworks**: [FastAPI](https://fastapi.tiangolo.com/), [LangGraph](https://langchain-ai.github.io/langgraph/), [LangChain](https://www.langchain.com/)
- **LLM Providers**: [Groq](https://groq.com/), [Hugging Face](https://huggingface.co/)
- **Database / ORM**: [PostgreSQL / Supabase](https://supabase.com/), [SQLAlchemy](https://www.sqlalchemy.org/), [psycopg2](https://www.psycopg.org/)
- **Package Manager**: [uv](https://docs.astral.sh/uv/)

---

## License

This project is licensed under the MIT License.
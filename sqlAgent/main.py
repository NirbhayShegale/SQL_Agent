import sys
import uuid
from pathlib import Path

src_path = Path(__file__).resolve().parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from Workflow.Graph import agent_app
from sqlagent.QueryWriter.QueryWriter import SQLQuery



def main() -> None:
    user_prompt = input("Enter your question: ").strip()
    if not user_prompt:
        raise SystemExit("Please enter a question.")

    thread_id = 12
    config = {"configurable": {"thread_id": thread_id}}
    result = agent_app.invoke({"user_prompt": user_prompt}, config=config)
    sql_query = result.get("sql_query")
    if sql_query is None:
        raise RuntimeError("The agent completed without generating a SQL query.")

    print(f"\nThread ID: {thread_id}")
    print("\nGenerated SQL:")
    print(sql_query.query if isinstance(sql_query, SQLQuery) else sql_query)


if __name__ == "__main__":
    main()

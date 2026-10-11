import sys
import uuid
from pathlib import Path

src_path = Path(__file__).resolve().parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from langgraph.types import Command
from Workflow.Graph import agent_app
from sqlagent.QueryWriter.QueryWriter import SQLQuery


def main() -> None:
    user_prompt = input("Enter your question: ").strip()
    if not user_prompt:
        raise SystemExit("Please enter a question.")

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    for event in agent_app.stream({"user_prompt": user_prompt}, config=config):
        print(event)

    while True:
        state = agent_app.get_state(config)
        if not state.next:
            break

        interrupts = [
            intr
            for task in state.tasks
            for intr in task.interrupts
        ]
        if not interrupts:
            break

        question = "Could you please clarify your request?"
        for intr in interrupts:
            if isinstance(intr.value, dict) and "question" in intr.value:
                question = intr.value["question"]
            elif isinstance(intr.value, str):
                question = intr.value
            else:
                question = str(intr.value)

        print(f"\nClarification needed: {question}")
        clarification = input("Your answer: ").strip()
        if not clarification:
            raise SystemExit("Please provide clarification.")

        for event in agent_app.stream(Command(resume=clarification), config=config):
            print(event)

    final_state = agent_app.get_state(config)
    sql_query = final_state.values.get("sql_query")

    print(f"\nThread ID: {thread_id}")
    if sql_query:
        sql_text = sql_query.query if isinstance(sql_query, SQLQuery) else str(sql_query)
        print(f"\nGenerated SQL:\n{sql_text}")
    else:
        print("\nAgent completed without generating a SQL query.")


if __name__ == "__main__":
    main()

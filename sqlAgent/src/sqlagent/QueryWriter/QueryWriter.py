from Config.LLm import QueryWriterLLM
from sqlagent.QueryWriter.QueryWriterPrompt import SYS_PROMPT_QUERY_WRITER
from pydantic import BaseModel, Field
from typing import TYPE_CHECKING
from collections.abc import Sequence

if TYPE_CHECKING:
    from Workflow.AgentState import AgentState

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langchain_core.exceptions import OutputParserException
from pydantic import ValidationError
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage

class SQLQuery(BaseModel):
    query: str = Field(
        description="A valid read-only PostgreSQL SQL query"
    )

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((OutputParserException, ValidationError, Exception)),
    reraise=True
)
def invoke_llm_with_retry(llm, messages):
    return llm.invoke(messages)

def QueryWriter(prompt: str, history: Sequence[AnyMessage] = ()) -> SQLQuery:

    messages = [
        SystemMessage(content=SYS_PROMPT_QUERY_WRITER),
        *history,
        HumanMessage(content=(
            "Use the conversation history as context for follow-up references, but treat "
            "the latest question as the request to answer. Generate a SQL query for: "
            f"{prompt}\nReturn the output strictly in JSON format."
        ))
    ]
    llm = QueryWriterLLM().with_structured_output(
        SQLQuery,
        method="json_mode"
    )

    response = invoke_llm_with_retry(llm, messages)
    return response

def sql_generation_node(state: "AgentState"):
    prompt = state["user_prompt"]
    result = QueryWriter(prompt, state.get("messages", []))

    return {
        "sql_query": result.query,
        "messages": [
            HumanMessage(content=prompt),
            AIMessage(content=result.model_dump_json()),
        ],
    }


# if __name__ == "__main__":
#     test = QueryWriter(
#         "What are the names and prices of all products in the "
#         "'Electronics' category that are currently in stock, "
#         "sorted by price in ascending order?"
#     )

#     print(test)
#     print(test.query)
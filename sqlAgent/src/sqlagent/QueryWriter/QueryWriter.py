from Config.LLm import QueryWriterLLM
from sqlagent.QueryWriter.QueryWriterPrompt import SYS_PROMPT_QUERY_WRITER
from pydantic import BaseModel, Field


class SQLQuery(BaseModel):
    query: str = Field(
        description="A valid read-only PostgreSQL SQL query"
    )


def QueryWriter(prompt: str) -> SQLQuery:

    message = (
        f"{SYS_PROMPT_QUERY_WRITER}\n\n"
        "Return your answer in valid JSON format with a single key named 'query'.\n"
        f"Use the database schema to create a SQL query "
        f"for the following question: {prompt}"
    )

    llm = QueryWriterLLM().with_structured_output(
        SQLQuery,
        method="json_mode"
    )

    response = llm.invoke(message)
    return response


# if __name__ == "__main__":
#     test = QueryWriter(
#         "What are the names and prices of all products in the "
#         "'Electronics' category that are currently in stock, "
#         "sorted by price in ascending order?"
#     )

#     print(test)
#     print(test.query)
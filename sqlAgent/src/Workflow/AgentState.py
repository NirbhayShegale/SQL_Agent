from typing import Annotated, Any, Optional, TypedDict
from langgraph.graph import add_messages
from langchain_core.messages import AnyMessage
from sqlagent.QueryWriter.QueryWriter import SQLQuery


class AgentState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]
    user_prompt: str
    schema_context: Optional[str]
    clarification_result: Optional[dict[str, Any]]
    sql_query: Optional[SQLQuery | str]
    next: Optional[str]
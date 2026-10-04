from typing import TypedDict, Optional, Any
from sqlagent.ClarificationEngine.ClarificationModel import ClarificationOutput
from sqlagent.QueryWriter.QueryWriter import SQLQuery

class AgentState(TypedDict, total=False):
    user_prompt: str
    schema_context: Optional[str]
    clarification_result: Optional[ClarificationOutput]
    sql_query: Optional[SQLQuery | str]
    next: Optional[str]
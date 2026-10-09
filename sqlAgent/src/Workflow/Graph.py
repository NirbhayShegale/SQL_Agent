from langgraph.graph import START, StateGraph, END
from Workflow.AgentState import AgentState
from Workflow.Router import route_after_clarification
from sqlagent.ClarificationEngine.ClarificationModel import (
    ask_human_node,
    clarification_node,
)
from sqlagent.QueryWriter.QueryWriter import sql_generation_node
from langgraph.checkpoint.memory import MemorySaver


workflow = StateGraph(AgentState)

workflow.add_node("clarify_query", clarification_node)
workflow.add_node("ask_human_node", ask_human_node)
workflow.add_node("generate_sql_node", sql_generation_node)

workflow.add_edge(START, "clarify_query")
workflow.add_conditional_edges(
    "clarify_query",
    route_after_clarification,
    {
        "generate_sql_node": "generate_sql_node",
        "ask_human_node": "ask_human_node",
    },
)
workflow.add_edge("ask_human_node", "clarify_query")

workflow.add_edge("generate_sql_node", END)

agent_app = workflow.compile(checkpointer=MemorySaver())

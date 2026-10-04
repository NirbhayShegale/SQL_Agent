from langgraph.graph import START, StateGraph, END
from Workflow.AgentState import AgentState
from Workflow.Router import route_after_clarification
from sqlagent.ClarificationEngine.ClarificationModel import clarification_node
from sqlagent.QueryWriter.QueryWriter import sql_generation_node
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver


# 1. Initialize Graph
workflow = StateGraph(AgentState)

# 2. Add Nodes
workflow.add_node("clarify_query", clarification_node)
workflow.add_node("generate_sql_node", sql_generation_node)


# 3. Define Entry Point
workflow.add_edge(START, "clarify_query")

# workflow.add_conditional_edges(
#     "clarify_query",
#     route_after_clarification,
#     {
#         "generate_sql_node": "generate_sql_node",
#         "ask_human_node": "ask_human_node"
#     }
# )

workflow.add_edge("clarify_query","generate_sql_node")
workflow.add_edge("generate_sql_node", END)

agent_app = workflow.compile(checkpointer=MemorySaver())
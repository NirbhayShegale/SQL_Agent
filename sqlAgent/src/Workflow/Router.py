from Workflow.AgentState import AgentState

def route_after_clarification(state: AgentState) -> str:
    """
    Evaluates the state and returns a string dictating the next step.
    """
    clarification_result = state.get("clarification_result")

    if not clarification_result:
        return "ask_human_node"

    if clarification_result.get("is_clear"):
        return "generate_sql_node"
    else:
        return "ask_human_node"
from Config.LLm import ClarificationEngineLLM
from sqlagent.ClarificationEngine.ClarificationPrompt import SYS_PROMPT_CLARIFICATION_ENGINE
from pydantic import BaseModel, Field
from typing import Optional, TYPE_CHECKING
from collections.abc import Sequence
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langgraph.types import interrupt

if TYPE_CHECKING:
    from Workflow.AgentState import AgentState

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langchain_core.exceptions import OutputParserException
from pydantic import ValidationError

class ClarificationOutput(BaseModel):
    is_clear: bool = Field(
        ...,
        description="True if the query is unambiguous and perfectly maps to the schema. False if it needs clarification."
    )
    reasoning: str = Field(
        ...,
        description="Internal thought process explaining exactly why the query is clear or ambiguous."
    )
    clarifying_question: Optional[str] = Field(
        default=None,
        description="The exact question to ask the user if is_clear is False. Must be null if is_clear is True."
    )

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((OutputParserException, ValidationError, Exception)),
    reraise=True
)
def invoke_llm_with_retry(llm, messages):
    return llm.invoke(messages)

def ClarificationEngine(
    prompt: str,
    history: Sequence[AnyMessage] = (),
) -> ClarificationOutput:

    messages = [
        SystemMessage(content=SYS_PROMPT_CLARIFICATION_ENGINE),
        *history,
        HumanMessage(content=(
            "Use the conversation history to understand follow-up references, but "
            "evaluate the latest question as the current request: "
            f"{prompt}\nReturn the output strictly in JSON format."
        ))
    ]

    llm = ClarificationEngineLLM().with_structured_output(
        ClarificationOutput,
        method="json_mode"
    )

    return invoke_llm_with_retry(llm, messages)


def clarification_node(state: "AgentState"):
    prompt = state["user_prompt"]
    result = ClarificationEngine(prompt, state.get("messages", []))

    return {
        "clarification_result": result.model_dump(),
        "messages": [
            HumanMessage(content=prompt),
            AIMessage(
                content=(
                    result.clarifying_question
                    if not result.is_clear and result.clarifying_question
                    else "Your request is clear."
                )
            ),
        ],
    }


def ask_human_node(state: "AgentState"):
    clarification = state.get("clarification_result")
    question = (
        clarification.get("clarifying_question")
        if clarification and clarification.get("clarifying_question")
        else "Could you clarify your request?"
    )
    answer = interrupt({"question": question})
    prompt = state["user_prompt"]

    return {
        "user_prompt": f"{prompt}\nUser clarification: {answer}",
        "messages": [HumanMessage(content=str(answer))],
    }


# if __name__ == "__main__":
#     test = ClarificationEngine(
#         "Show me the top 10 best performing products from last month."
#     )

#     print(test)
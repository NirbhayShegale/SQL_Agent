from Config.LLm import ClarificationEngineLLM
from sqlagent.ClarificationEngine.ClarificationPrompt import SYS_PROMPT_CLARIFICATION_ENGINE
from pydantic import BaseModel, Field
from typing import Optional, TYPE_CHECKING
from langchain_core.messages import SystemMessage, HumanMessage

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

def ClarificationEngine(prompt: str) -> ClarificationOutput:

    messages = [
        SystemMessage(content=SYS_PROMPT_CLARIFICATION_ENGINE),
        HumanMessage(content=f"Use the database schema to create a clarification query for the following question: {prompt}. You must return the output strictly in JSON format.")
    ]

    llm = ClarificationEngineLLM().with_structured_output(
        ClarificationOutput,
        method="json_mode"
    )

    try:
        # Execute with Tenacity retry logic
        response = invoke_llm_with_retry(llm, messages)
        return response
        
    except Exception as e:        
        return ClarificationOutput(
            is_clear=False,
            reasoning=f"The LLM completely failed to parse the output into valid JSON after multiple retries.\nerror{e}",
            clarifying_question="I encountered an internal system error while analyzing your request. Could you please rephrase it?"
        )


def clarification_node(state: "AgentState"):
    prompt = state["user_prompt"]
    result = ClarificationEngine(prompt)

    return {"clarification_result": result}


# if __name__ == "__main__":
#     test = ClarificationEngine(
#         "Show me the top 10 best performing products from last month."
#     )

#     print(test)
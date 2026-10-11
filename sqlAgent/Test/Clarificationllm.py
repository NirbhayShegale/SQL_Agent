from sqlagent.ClarificationEngine.ClarificationModel import ClarificationEngine, ClarificationOutput

test_prompt="What is the capital of Japan?"

test_result = ClarificationEngine(test_prompt)
print(test_result)


from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def QueryWriterLLM():
    return ChatGroq(
        model="qwen/qwen3.8-27b",
        temperature=0.0,
    )

# print(QueryWriterLLM().invoke('What are the names and prices of all products in the "Electronics" category that are currently in stock, sorted by price in ascending order?'))

def ClarificationEngineLLM():
    return ChatGroq(
        model="qwen/qwen3.8-27b",
        temperature=0.0,
    )

# print(ClarificationEngineLLM().invoke('What are the names and prices of all products in the "Electronics" category that are currently in stock, sorted by price in ascending order?'))
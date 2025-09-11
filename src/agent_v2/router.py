import os
from typing import Literal
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama.chat_models import ChatOllama

# Load environment variables
load_dotenv()

# --- LLM Initialization for Router ---
# To switch to a local Ollama model, comment out the Google LLM
# and uncomment the Ollama LLM.

# Google Gemini LLM (requires API key)
api_key = os.getenv("GEMINI_API_KEY")
router_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0, google_api_key=api_key)

# Ollama LLM (local, no API key required)
# router_llm = ChatOllama(model="llama3", temperature=0)

# Define the Pydantic model for the router's output.
# This forces the LLM to choose one of the specified datasources.
class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""
    datasource: Literal["RAG", "SQL", "External Help", "General"] = Field(
        ...,
        description="Given a user query, select the most appropriate datasource to handle it."
    )

# Create a structured LLM by binding the Pydantic model to the LLM.
# This makes the LLM's output structured according to our RouteQuery model.
structured_llm_router = router_llm.with_structured_output(RouteQuery)

# Create the prompt for the router.
# This prompt guides the LLM on how to make the routing decision.
router_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """You are an expert at routing a user question to the appropriate data source.
Based on the user's query, select the best data source from the available options.

Here are the descriptions of the datasources:
- **RAG**: Use for questions about college policies, academic calendars, fee structures, and other general information found in official documents. For example: "What are the library hours?", "When is the fee deadline?".
- **SQL**: Use for questions about specific, real-time events, schedules, or data that would be in a database. For example: "Are there any events today?", "What workshops are scheduled for next week?".
- **External Help**: Use when the user is explicitly asking for contact information or how to speak to a human. For example: "Who do I talk to about my exam results?", "I need help with admissions."
- **General**: Use for conversational questions, greetings, or any query that does not fit the other categories. For example: "Hello", "What is AI?", "Tell me a joke."."""),
        ("user", "Question: {question}"),
    ]
)

# Create the final router chain.
# It takes the input dict, pipes it to the prompt, then to the structured LLM.
# The output will be an instance of the RouteQuery class.
query_router = (
    {"question": lambda x: x["refined_query"]}
    | router_prompt
    | structured_llm_router
)

import pytest
from src.agent_v2.graph import app as agent_app
from langchain_core.messages import AIMessage, HumanMessage

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

def run_agent_and_get_final_state(query: str, language: str = "en", chat_history: list = None) -> dict:
    """
    Helper function to run the agent and get the final state.
    It now accepts an optional chat_history list.
    """
    inputs = {
        "original_query": query,
        "language": language,
        "chat_history": chat_history or [],
    }
    final_state = None
    # The stream method yields the state at each step. The last one is the final state.
    for event in agent_app.stream(inputs):
        final_state = event

    if not final_state:
        pytest.fail("The agent did not produce a final state.")

    # The final state is a dict where the key is the last node's name.
    # We return the value, which is the AgentState dictionary.
    return list(final_state.values())[0]

@pytest.mark.asyncio
async def test_rag_route_english():
    """Tests the RAG route for a question that should be in the documents."""
    query = "What is the deadline for semester fee payment?"
    result_state = run_agent_and_get_final_state(query)

    assert result_state["source"] == "RAG"
    assert "fee" in result_state["answer"].lower()
    assert "deadline" in result_state["answer"].lower()

@pytest.mark.asyncio
async def test_sql_route_english():
    """Tests the SQL route for a question about events."""
    query = "What events are happening on October 10th, 2025?"
    result_state = run_agent_and_get_final_state(query)

    assert result_state["source"] == "SQL"
    assert "Tech Fest" in result_state["answer"]
    assert "CodeClash" in result_state["answer"]

@pytest.mark.asyncio
async def test_help_route_english():
    """Tests the External Help route for a query asking for a contact."""
    query = "Who do I talk to about my exam results?"
    result_state = run_agent_and_get_final_state(query)

    assert result_state["source"] == "External Help"
    assert "Examinations Department" in result_state["answer"]
    assert "exams@examplecollege.edu" in result_state["answer"]

@pytest.mark.asyncio
async def test_general_route_english():
    """Tests the General QA route with a simple greeting."""
    query = "Hello there"
    result_state = run_agent_and_get_final_state(query)

    assert result_state["source"] == "General"
    assert "hello" in result_state["answer"].lower()

@pytest.mark.asyncio
async def test_translation_and_rag_route_hindi():
    """Tests the full translation -> RAG -> translation flow with a Hindi query."""
    query = "फीस भुगतान की अंतिम तिथि कब है?"
    result_state = run_agent_and_get_final_state(query, language="hi")

    assert result_state["source"] == "RAG"
    assert result_state["answer"].isascii() is False
    assert "शुल्क" in result_state["answer"] or "अंतिम" in result_state["answer"]

@pytest.mark.asyncio
async def test_conversation_with_memory():
    """Tests that the agent can handle a follow-up question using memory."""
    # Define a simulated chat history
    chat_history = [
        HumanMessage(content="Are there any events related to technology?"),
        AIMessage(content="Yes, on October 10th, 2025, there are two tech-related events: the Tech Fest 2025 and the CodeClash Coding Competition."),
    ]

    # Ask a follow-up question that relies on the history
    follow_up_query = "Which one of those is a competition?"

    result_state = run_agent_and_get_final_state(follow_up_query, chat_history=chat_history)

    # The agent should refine the query to be about the "CodeClash" event and route to SQL or RAG
    # A good response should specifically mention the competition.
    assert "CodeClash" in result_state["answer"]
    assert "Tech Fest" not in result_state["answer"] # Check that it's specific

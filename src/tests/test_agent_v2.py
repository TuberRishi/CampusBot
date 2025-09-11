import pytest
from src.agent_v2.graph import app as agent_app

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

def run_agent_and_get_final_state(query: str, language: str = "en") -> dict:
    """Helper function to run the agent and get the final state."""
    inputs = {"original_query": query, "language": language}
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
    # Query: "फीस भुगतान की अंतिम तिथि कब है?" (When is the fee payment deadline?)
    query = "फीस भुगतान की अंतिम तिथि कब है?"
    result_state = run_agent_and_get_final_state(query, language="hi")

    assert result_state["source"] == "RAG"
    # The final answer should be translated back to Hindi.
    # A simple check is to ensure it's not the default English answer and contains non-ASCII chars.
    assert result_state["answer"].isascii() is False
    # A more specific check could look for Hindi words.
    # "शुल्क" (shulk) means fee. "अंतिम" (antim) means last/final.
    assert "शुल्क" in result_state["answer"] or "अंतिम" in result_state["answer"]

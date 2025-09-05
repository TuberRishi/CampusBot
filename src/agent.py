import os
import json
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.tools import Tool
from langgraph.prebuilt import ToolExecutor
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage

from src.tools.sql_tool import get_sql_tools

# --- Load Environment Variables ---
load_dotenv()

# --- Configuration ---
FAISS_PATH = "faiss_index"
EMBEDDING_MODEL_NAME = "models/text-embedding-004"
LLM_MODEL_NAME = "models/gemini-1.5-flash-latest"
DEPARTMENT_MAPPING_PATH = "src/department_mapping.json"
# This is now a DISTANCE threshold for L2 distance. Lower is better.
# A value of 0.7 is a reasonable starting point.
DISTANCE_THRESHOLD = 0.7

def load_fallback_data():
    """Loads the department mapping for the fallback mechanism."""
    with open(DEPARTMENT_MAPPING_PATH, 'r') as f:
        return json.load(f)

def create_custom_rag_tool(retriever):
    """
    Creates a custom tool for the RAG retriever that checks a similarity score threshold.
    """
    def search_with_threshold(query: str) -> str:
        """
        Performs a similarity search and returns document content only if the
        similarity score of the top result is above a certain threshold.
        """
        print(f"Performing similarity search for: '{query}'")
        # We are using the default L2 distance. A lower score is better.
        docs_with_scores = retriever.vectorstore.similarity_search_with_score(query, k=1)

        if not docs_with_scores:
            return "No relevant information found."

        top_doc, score = docs_with_scores[0]
        print(f"Top document L2 distance: {score}")

        if score > DISTANCE_THRESHOLD:
            return "No relevant information found. The retrieved document is not similar enough."

        # If score is good, return the content of the top k documents from a standard search
        docs = retriever.get_relevant_documents(query)
        return "\n\n".join([doc.page_content for doc in docs])

    return Tool(
        name="search_college_documents",
        func=search_with_threshold,
        description="Searches and returns information from college documents like circulars and notices. Use it for questions about fees, deadlines, academic calendar, etc."
    )

class AgentState(TypedDict):
    """
    Represents the state of our agent. It's a list of messages.
    The `operator.add` in the graph transitions will append messages to this list.
    """
    messages: Annotated[Sequence[BaseMessage], operator.add]

def create_agent_executor():
    """
    Creates the main LangGraph-based agent executor.
    """
    print("Initializing LangGraph agent...")

    # --- Initialize Model ---
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME, google_api_key=api_key)
    print(f"LLM '{LLM_MODEL_NAME}' initialized.")

    # --- Initialize Tools ---
    # 1. RAG Tool
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL_NAME, google_api_key=api_key)
    faiss_index = FAISS.load_local(FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    retriever = faiss_index.as_retriever(search_type="mmr", search_kwargs={'k': 4, 'fetch_k': 20})
    rag_tool = create_custom_rag_tool(retriever)

    # 2. SQL Tools
    sql_tools = get_sql_tools()

    # 3. Combine and create the executor
    all_tools = [rag_tool] + sql_tools
    tool_executor = ToolExecutor(all_tools)
    print(f"Created ToolExecutor with {len(all_tools)} tools.")

    # --- Define Agent Logic as Graph Nodes ---

    # Bind the tools to the LLM so it knows how to call them
    model_with_tools = llm.bind_tools(all_tools)

    def should_continue(state: AgentState):
        """
        Router function to decide the next step.
        If the last message is a tool call, execute the tool. Otherwise, end.
        """
        last_message = state['messages'][-1]
        if last_message.tool_calls:
            return "continue" # Branch to the tool execution node
        return "end" # End the graph

    def call_model(state: AgentState):
        """
        The main agent node. Invokes the LLM with the current state.
        The response is added to the list of messages.
        """
        response = model_with_tools.invoke(state['messages'])
        return {"messages": [response]}

    def call_tool(state: AgentState):
        """
        The tool execution node. It takes the last message, which must be a
        tool call, executes the tool, and returns the tool's output
        as a new ToolMessage.
        """
        last_message = state['messages'][-1]
        action = last_message.tool_calls[0]
        tool_output = tool_executor.invoke(action)
        # The state transition will append this to the message list
        return {"messages": [tool_output]}

    # --- Build the Graph ---
    print("Building the agent graph...")
    workflow = StateGraph(AgentState)

    # Add the nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("action", call_tool)

    # Define the entry point and edges
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "action",
            "end": END
        }
    )
    workflow.add_edge('action', 'agent')

    # Compile the graph into a runnable object
    graph = workflow.compile()
    print("Agent graph compiled successfully.")

    return graph

def run_agent_tests():
    """
    Runs a series of predefined tests against the agent executor.
    """
    executor = create_agent_executor()
    print("\n--- Running Agent Tests ---")

    test_queries = [
        "When is the deadline for semester fee payment?",
        "What is the capital of Nepal?" # Should fail due to low similarity score
    ]

    for i, query in enumerate(test_queries):
        print(f"\n--- Test {i+1}: Query: '{query}' ---")
        try:
            response = executor.invoke({"input": query})
            print("\nAgent Response:")
            print(response)
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    run_agent_tests()

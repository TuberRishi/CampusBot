import os
import json
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain.tools import Tool

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

# --- Agent Prompt Template ---
AGENT_PROMPT_TEMPLATE = """
You are a helpful and friendly AI assistant for the students of Example College.
Your name is CampusBot. Your goal is to provide accurate answers based ONLY on the context provided by your available tools.

You have access to the following tools:
{tools}

**Instructions:**
1.  Read the user's query carefully.
2.  Select the best tool to answer the user's query. The 'search_college_documents' tool is your primary source of information.
3.  Synthesize an answer directly from the information returned by the tool. Do not use any prior knowledge.
4.  If the tool returns a valid answer, provide it in a clear and concise manner.
5.  If the tool indicates that no relevant information was found, or if you cannot find an answer in the tool's output, you MUST respond with the exact phrase: "I do not have enough information to answer that question." Do not try to guess the answer.
6.  Be friendly and approachable in your tone.

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""

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

def create_agent_executor():
    """
    Creates the main LangChain agent and its executor.
    """
    print("Initializing RAG-only agent with custom tool...")

    # 1. Initialize LLM
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL_NAME, google_api_key=api_key)
    print(f"LLM '{LLM_MODEL_NAME}' initialized.")

    # 2. Load the RAG retriever with MMR
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL_NAME, google_api_key=api_key)
    faiss_index = FAISS.load_local(FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    retriever = faiss_index.as_retriever(
        search_type="mmr",
        search_kwargs={'k': 4, 'fetch_k': 20} # Fetch more docs for MMR to work on
    )
    print("RAG retriever with MMR created.")

    # 3. Create the custom tool with the score threshold
    custom_retriever_tool = create_custom_rag_tool(retriever)
    all_tools = [custom_retriever_tool]
    print("Custom RAG tool with similarity threshold created.")

    # 4. Create the agent prompt
    prompt = PromptTemplate.from_template(AGENT_PROMPT_TEMPLATE)

    # 5. Create the agent
    agent = create_react_agent(llm, all_tools, prompt)
    print("ReAct agent created.")

    # 6. Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=all_tools,
        verbose=True,
        handle_parsing_errors=True
    )
    print("Agent Executor created.")

    return agent_executor

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

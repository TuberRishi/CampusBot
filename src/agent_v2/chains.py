import os
from typing import Dict, Any
from dotenv import load_dotenv

from google.cloud import translate_v2 as translate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough, RunnableBranch
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Load environment variables from .env file
load_dotenv()

# Initialize the Google Translate client
# It should automatically use the credentials set up by the API key
try:
    translate_client = translate.Client()
    print("Google Translate client initialized successfully.")
except Exception as e:
    print(f"Warning: Could not initialize Google Translate client. Error: {e}")
    translate_client = None

# Initialize the LLM from environment variables
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Warning: GEMINI_API_KEY not found in .env file. LLM will likely fail.")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0, google_api_key=api_key)


def detect_language_chain(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects the language of the user's query.

    Args:
        state: The current agent state, which must contain 'original_query'.

    Returns:
        A dictionary with the detected language code (e.g., 'en', 'hi').
    """
    query = state.get("original_query", "")

    if not translate_client or not query.strip():
        # Default to English if client fails or query is empty
        return {"language": "en"}

    try:
        # The detect_language result is a dict e.g., {'language': 'en', 'confidence': 1}
        result = translate_client.detect_language(query)
        language = result["language"]
        print(f"Detected language: {language} for query: '{query}'")
    except Exception as e:
        print(f"Error during language detection: {e}. Defaulting to 'en'.")
        language = "en"  # Default to English on API error

    return {"language": language}


# --- Query Refinement Chain ---

# Prompt template for the LLM to refine the query
refine_query_prompt_template = ChatPromptTemplate.from_template(
    """You are an expert in understanding and refining user queries for a university chatbot.
Your task is to take a user's query and rephrase it into a clear, specific, and searchable English query.

- If the query is in a language other than English, you MUST translate it to English.
- If the query is a simple greeting (e.g., "hello", "hi"), return it as is, in English.
- For all other queries, refine them to be optimal for a database search or a vector store lookup.
- Be concise and focus on the key intent.

Original Query:
```{original_query}```

Refined English Query:"""
)

# This is the main refinement chain that uses the LLM
llm_refinement_chain = (
    refine_query_prompt_template
    | llm
    | (lambda msg: {"refined_query": msg.content})  # Extract content from AIMessage
)


def get_refine_query_chain() -> Runnable:
    """
    Creates a chain that intelligently refines the user's query.

    It uses a RunnableBranch to decide on the refinement strategy:
    1. Pass through simple English greetings without change.
    2. Use an LLM to translate and refine all non-English queries.
    3. Use an LLM to refine all other substantial English queries.
    """
    greetings = ["hello", "hi", "hey", "thanks", "thank you", "namaste", "hola"]

    # A simple chain to pass the query through without refinement, just structuring the output
    passthrough_chain = RunnablePassthrough.assign(
        refined_query=lambda x: x["original_query"]
    )

    refinement_branch = RunnableBranch(
        # If the original query (in lowercase) is a simple greeting, pass it through.
        (
            lambda x: x["original_query"].strip().lower() in greetings,
            passthrough_chain,
        ),
        # Default case: For all other queries (non-greetings or non-English),
        # use the LLM to refine and/or translate.
        llm_refinement_chain,
    )
    return refinement_branch


# Instantiate the chain for use in the graph
refine_query_chain = get_refine_query_chain()


# --- RAG Chain Implementation ---

from langchain_community.vectorstores import FAISS

# Configuration
FAISS_PATH = "faiss_index"
EMBEDDING_MODEL_NAME = "models/text-embedding-004"
DISTANCE_THRESHOLD = 0.7  # L2 distance, lower is better

# Load the vector store and retriever once
try:
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL_NAME)
    faiss_index = FAISS.load_local(
        FAISS_PATH, embeddings, allow_dangerous_deserialization=True
    )
    retriever = faiss_index.as_retriever(
        search_type="mmr", search_kwargs={"k": 4, "fetch_k": 20}
    )
    print("FAISS vector store loaded successfully for RAG chain.")
except Exception as e:
    print(f"Error loading FAISS index for RAG chain: {e}")
    retriever = None

rag_prompt_template = ChatPromptTemplate.from_template(
    """You are a helpful university assistant. Your name is CampusBot.
Answer the user's question based ONLY on the following context.
If the context does not contain the answer, state that you don't have enough information.

Context:
{context}

Question:
{question}

Answer:"""
)

def retrieve_documents(query: str) -> str:
    """
    Retrieves relevant documents from the vector store, checking a similarity threshold.
    """
    if not retriever:
        return "Error: Document retriever is not available."

    # Use the retriever to find documents with scores
    docs_with_scores = retriever.vectorstore.similarity_search_with_score(query, k=1)
    if not docs_with_scores:
        return "No relevant information found in college documents."

    # The method returns a list of (Document, score) tuples.
    doc, score = docs_with_scores[0]

    # The score from similarity_search_with_score is distance. Lower is better.
    if score > DISTANCE_THRESHOLD:
        print(f"RAG threshold not met. Score: {score} > {DISTANCE_THRESHOLD}")
        return "No relevant information found. The retrieved documents are not similar enough to the query."

    # If the top document is relevant enough, get the full set of documents to use as context
    docs = retriever.get_relevant_documents(query)
    return "\n\n".join([doc.page_content for doc in docs])


# Create the full RAG chain using LCEL
rag_chain = (
    {
        "context": lambda x: retrieve_documents(x["refined_query"]),
        "question": lambda x: x["refined_query"],
    }
    | rag_prompt_template
    | llm
    | (lambda msg: {"answer": msg.content, "source": "RAG"})
)


# --- General QA Chain ---

# A prompt for general, conversational questions
general_qa_prompt = ChatPromptTemplate.from_template(
    """You are a helpful and friendly university AI assistant named CampusBot.
Answer the user's question conversationally and to the best of your ability.

Question: {question}

Answer:"""
)

# The final chain for general questions
general_qa_chain = (
    {"question": (lambda x: x["refined_query"])}
    | general_qa_prompt
    | llm
    | (lambda msg: {"answer": msg.content, "source": "General"})
)


# --- SQL Chain Implementation ---

from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool

# Initialize DB and tools
try:
    db = SQLDatabase.from_uri(f"sqlite:///college_events.db")
    execute_query_tool = QuerySQLDatabaseTool(db=db)
    write_query_chain = create_sql_query_chain(llm, db)
    print("SQL Database tools initialized successfully for SQL chain.")
except Exception as e:
    print(f"Error initializing SQL Database tools for SQL chain: {e}")
    db = None
    execute_query_tool = None
    write_query_chain = None

# Prompt to generate a final answer from the SQL result
sql_answer_prompt = ChatPromptTemplate.from_template(
    """You are a helpful university assistant. Your name is CampusBot.
Synthesize a natural language answer for the user based on the SQL query result and the original question.
If the SQL result is empty or indicates an error, state that you couldn't find the information in the database.

SQL Query Result:
{sql_result}

Original Question:
{question}

Answer:"""
)

def run_and_format_sql(state: dict) -> dict:
    """
    A helper function to run the SQL query and then format the final answer.
    This combines multiple steps into one logical unit.
    """
    # Generate the SQL query string
    sql_query = write_query_chain.invoke({"question": state["refined_query"]})
    print(f"---DEBUG: Generated SQL Query: {sql_query} ---") # DEBUG

    # Execute the SQL query
    sql_result = execute_query_tool.invoke(sql_query)

    # Generate the final natural language answer
    final_answer_chain = sql_answer_prompt | llm
    final_answer = final_answer_chain.invoke({
        "sql_result": sql_result,
        "question": state["refined_query"]
    })

    return {"answer": final_answer.content, "source": "SQL"}

# The final SQL chain is now just a single runnable function
sql_chain = run_and_format_sql


# --- External Help Chain ---

import json

# Load the department mapping data
try:
    with open("src/department_mapping.json", "r") as f:
        department_data = json.load(f)
    # Get all unique keywords, excluding 'default' for the prompt
    department_keywords = [k for k in department_data.keys() if k != "default"]
    print("Department mapping loaded successfully for External Help chain.")
except Exception as e:
    print(f"Error loading department mapping for External Help chain: {e}")
    department_data = {}
    department_keywords = []

# Prompt to extract the most relevant department keyword
help_keyword_prompt = ChatPromptTemplate.from_template(
    """You are an expert at routing student queries to the correct department.
Based on the user's question, identify the single most relevant department keyword from the provided list.
If no keyword seems directly relevant, you MUST respond with the single word "default".

Available Department Keywords: {keywords}

Question: {question}

Most Relevant Keyword:"""
)

def get_department_contact(keyword: str) -> str:
    """Looks up a department's contact info from the loaded JSON data and formats it."""
    # Clean up the LLM output
    keyword = keyword.strip().lower().replace("'", "").replace('"', '')

    # Get the contact info, falling back to the default if the keyword is not found
    contact_info = department_data.get(keyword, department_data.get("default", {}))

    if not contact_info:
        return "I am sorry, but I could not find any contact information for your query."

    return (
        f"For questions like this, it's best to contact the {contact_info.get('name', 'N/A')}. "
        f"You can reach them at:\n"
        f"- Email: {contact_info.get('email', 'N/A')}\n"
        f"- Location: {contact_info.get('location', 'N/A')}"
    )

# Create the full External Help chain
external_help_chain = (
    {
        "question": (lambda x: x["refined_query"]),
        "keywords": (lambda x: ", ".join(department_keywords)),
    }
    | help_keyword_prompt
    | llm
    | (lambda msg: {"answer": get_department_contact(msg.content), "source": "External Help"})
)

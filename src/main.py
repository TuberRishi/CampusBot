import os
import secrets
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

from src.agent import create_agent_executor, load_fallback_data
from src.ingest import main as run_ingestion

# --- Environment and Security ---
load_dotenv()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

async def verify_admin_password(x_admin_password: str = Header(None)):
    """
    Dependency to verify the admin password.
    """
    if not ADMIN_PASSWORD:
        raise HTTPException(status_code=500, detail="Admin password not configured on server.")
    if not x_admin_password:
        raise HTTPException(status_code=401, detail="X-Admin-Password header missing.")

    if not secrets.compare_digest(x_admin_password, ADMIN_PASSWORD):
        raise HTTPException(status_code=403, detail="Incorrect admin password.")

# --- FastAPI App Initialization ---
app = FastAPI(
    title="College Chatbot API",
    description="An API for the multilingual college chatbot.",
    version="1.0.0"
)

# --- CORS Middleware ---
# This allows the frontend (running on a different origin) to communicate with the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for simplicity in development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Data Models ---
class ChatRequest(BaseModel):
    query: str
    language: str = "en" # Default to English

class ChatResponse(BaseModel):
    answer: str
    source: str # e.g., "agent", "fallback"

# --- Global Variables ---
# Load the agent and fallback data once on startup
agent_executor = None
fallback_data = None

@app.on_event("startup")
def startup_event():
    """
    Load the agent and fallback data when the server starts.
    """
    global agent_executor, fallback_data
    print("Server starting up...")
    agent_executor = create_agent_executor()
    fallback_data = load_fallback_data()
    print("Agent and fallback data loaded. Server is ready.")

# --- API Endpoints ---
# --- System Prompt for the Agent ---
SYSTEM_PROMPT = """
You are a helpful and friendly AI assistant for the students of Example College.
Your name is CampusBot. Your goal is to provide accurate answers based ONLY on the context provided by your available tools.

You have access to two kinds of tools:
1.  `search_college_documents`: Use this to find information in the college's official documents, like circulars, notices, and FAQs. This is your primary source for questions about policies, fees, deadlines, etc.
2.  `sql_db_*`: Use these tools to query the college's events database. This is useful for questions about specific events, dates, and locations (e.g., "When is Tech Fest?").

**Instructions:**
1.  Read the user's query carefully.
2.  Select the best tool to answer the query.
3.  Synthesize an answer directly from the information returned by the tool. Do not use any prior knowledge.
4.  If no tool provides a relevant answer, respond that you don't have enough information. Do not try to guess.
5.  If the query is a general greeting or question (e.g., "hello", "who are you?"), answer it naturally without using a tool.
6.  Be friendly and approachable in your tone.
"""

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main endpoint for handling chat requests using the LangGraph agent.
    """
    if not agent_executor:
        raise HTTPException(status_code=503, detail="Agent is not initialized. Please wait.")

    print(f"Received query: '{request.query}' in language '{request.language}'")

    # TODO: Implement translation logic here
    query_to_agent = request.query

    # 1. Construct the message list for the LangGraph agent
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=query_to_agent)
    ]

    # 2. Invoke the agent
    try:
        # The input to the graph is a dictionary with the 'messages' key
        response = agent_executor.invoke({"messages": messages})
        # The final answer is in the `content` of the last message
        agent_answer = response['messages'][-1].content
    except Exception as e:
        print(f"Error invoking agent: {e}")
        raise HTTPException(status_code=500, detail="An error occurred with the agent.")

    # 3. Implement the fallback logic (can be simplified or improved later)
    # This check might need to be updated depending on the new agent's "I don't know" responses.
    if "i do not have enough information" in agent_answer.lower() or "don't have information" in agent_answer.lower():
        print("Agent could not find an answer. Triggering fallback.")

        # Simple keyword-based fallback
        for keyword, department_info in fallback_data.items():
            if keyword in query_to_agent.lower():
                fallback_answer = (
                    f"I couldn't find a specific answer for that. "
                    f"For questions related to '{keyword}', you can contact the {department_info['name']}. "
                    f"You can reach them at {department_info['email']} or visit them at {department_info['location']}."
                )
                final_answer = fallback_answer
                source = "fallback"
                break
        else: # If no keyword matches
            fallback_answer = (
                "I'm sorry, I couldn't find an answer to your question, and I'm not sure which department to direct you to. "
                "Please contact the main Student Support Office for assistance."
            )
            final_answer = fallback_answer
            source = "fallback"

    else:
        final_answer = agent_answer
        source = "agent"

    # TODO: Implement translation logic here
    # 4. Translate final_answer back to the original language if needed

    return ChatResponse(answer=final_answer, source=source)


# --- Admin Endpoints ---
@app.post("/admin/rebuild-index", status_code=200, dependencies=[Depends(verify_admin_password)])
async def admin_rebuild_index():
    """
    Admin endpoint to manually trigger the rebuilding of the FAISS index.
    Requires a valid password in the 'X-Admin-Password' header.
    """
    try:
        print("Starting index rebuild process from API endpoint...")
        run_ingestion()
        print("Index rebuild process finished successfully.")
        # We need to reload the agent executor so the chatbot uses the new index
        global agent_executor
        agent_executor = create_agent_executor()
        print("Agent executor reloaded with new index.")
        return {"message": "Knowledge base index rebuilt and reloaded successfully."}
    except Exception as e:
        print(f"Error during index rebuild: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to rebuild index: {str(e)}")


if __name__ == "__main__":
    # This allows running the server directly for testing
    # uvicorn src.main:app --reload
    print("To run the API server, use the command:")
    print("uvicorn src.main:app --reload")
    uvicorn.run(app, host="0.0.0.0", port=8000)

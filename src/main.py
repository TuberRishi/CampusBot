import uvicorn
import uuid
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import AIMessage, HumanMessage

# Import the new LangGraph agent application
from src.agent_v2.graph import app as agent_app

# --- FastAPI App Initialization ---
app = FastAPI(
    title="CampusBot API v2",
    description="An API for the multilingual, multi-tool college chatbot.",
    version="2.0.0",
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-Memory Session Store ---
# NOTE: This is for demonstration only. In production, use a proper database or cache like Redis.
session_store = {}

# --- Data Models ---
class ChatRequest(BaseModel):
    query: str
    session_id: str | None = None  # Client can send a session_id to maintain context
    language: str = "en"

class ChatResponse(BaseModel):
    answer: str
    source: str
    session_id: str  # Server will always return a session_id

# --- Startup Event ---
@app.on_event("startup")
def startup_event():
    """Log a message when the server starts."""
    print("Server starting up... The agent graph is ready.")

# --- API Endpoints ---
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main endpoint for handling chat requests. It now manages conversation history.
    """
    session_id = request.session_id or str(uuid.uuid4())
    print(f"Received query: '{request.query}' in session '{session_id}'")

    # Retrieve chat history from the session store or create an empty list
    chat_history = session_store.get(session_id, [])

    # The initial state for the graph, now including chat history
    inputs = {
        "original_query": request.query,
        "language": request.language,
        "chat_history": chat_history,
    }

    try:
        # Stream the events from the graph
        final_state = None
        for event in agent_app.stream(inputs):
            final_state = event

        if not final_state:
            raise HTTPException(status_code=500, detail="Agent did not produce an output.")

        agent_state = list(final_state.values())[0]
        final_answer = agent_state.get("answer", "I'm sorry, something went wrong.")
        source = agent_state.get("source", "error")

        # Update the history with the new user query and AI response
        # We use HumanMessage and AIMessage to structure the history correctly
        updated_history = chat_history + [
            HumanMessage(content=request.query),
            AIMessage(content=final_answer),
        ]
        session_store[session_id] = updated_history

        print(f"Final answer: '{final_answer}', Source: '{source}'")
        return ChatResponse(answer=final_answer, source=source, session_id=session_id)

    except Exception as e:
        print(f"Error invoking agent graph: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred with the agent: {e}")

if __name__ == "__main__":
    print("To run the API server, use the command:")
    print("uvicorn src.main:app --reload")
    uvicorn.run(app, host="0.0.0.0", port=8000)

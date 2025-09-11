from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import the new LangGraph agent application
from src.agent_v2.graph import app as agent_app

# --- FastAPI App Initialization ---
app = FastAPI(
    title="CampusBot API v2",
    description="An API for the multilingual, multi-tool college chatbot.",
    version="2.0.0"
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class ChatRequest(BaseModel):
    query: str
    # The language code is now directly used by the agent graph
    language: str = "en"

class ChatResponse(BaseModel):
    answer: str
    source: str # e.g., "RAG", "SQL", "External Help", "General"

# --- Startup Event ---
@app.on_event("startup")
def startup_event():
    """
    Log a message when the server starts.
    All expensive resources are now lazy-loaded within the agent's modules.
    """
    print("Server starting up... The agent graph is ready.")
    # You can optionally invoke the graph once to "warm it up"
    # list(agent_app.stream({"original_query": "hello", "language": "en"}))
    # print("Agent pre-warmed.")


# --- API Endpoints ---
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main endpoint for handling chat requests with the new LangGraph agent.
    """
    print(f"Received query: '{request.query}' in language '{request.language}'")

    # The initial state for the graph
    inputs = {"original_query": request.query, "language": request.language}

    try:
        # Stream the events from the graph
        # The final state is the last event from the stream
        final_state = None
        for event in agent_app.stream(inputs):
            final_state = event

        if not final_state:
            raise HTTPException(status_code=500, detail="Agent did not produce an output.")

        # The final state is a dictionary where the key is the last node that ran
        # and the value is the AgentState. We just need the state.
        agent_state = list(final_state.values())[0]

        final_answer = agent_state.get("answer", "I'm sorry, something went wrong.")
        source = agent_state.get("source", "error")

        print(f"Final answer: '{final_answer}', Source: '{source}'")
        return ChatResponse(answer=final_answer, source=source)

    except Exception as e:
        print(f"Error invoking agent graph: {e}")
        # Be careful about exposing internal errors to the client
        raise HTTPException(status_code=500, detail=f"An error occurred with the agent: {e}")

if __name__ == "__main__":
    print("To run the API server, use the command:")
    print("uvicorn src.main:app --reload")
    uvicorn.run(app, host="0.0.0.0", port=8000)

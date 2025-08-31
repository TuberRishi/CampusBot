import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from src.agent import create_agent_executor, load_fallback_data

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
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main endpoint for handling chat requests.
    """
    if not agent_executor:
        raise HTTPException(status_code=503, detail="Agent is not initialized. Please wait.")

    print(f"Received query: '{request.query}' in language '{request.language}'")

    # TODO: Implement translation logic here
    # 1. Translate query to English if language is not 'en'
    query_to_agent = request.query

    # 2. Invoke the agent
    try:
        response = agent_executor.invoke({"input": query_to_agent})
        agent_answer = response.get("output", "")
    except Exception as e:
        print(f"Error invoking agent: {e}")
        raise HTTPException(status_code=500, detail="An error occurred with the agent.")

    # 3. Implement the fallback logic
    if "i do not have enough information" in agent_answer.lower():
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

if __name__ == "__main__":
    # This allows running the server directly for testing
    # uvicorn src.main:app --reload
    print("To run the API server, use the command:")
    print("uvicorn src.main:app --reload")
    uvicorn.run(app, host="0.0.0.0", port=8000)

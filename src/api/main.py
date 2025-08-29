import os
import asyncio
import shutil
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware  # Import the CORS middleware
from contextlib import asynccontextmanager

from src.api.models import AskRequest, AskResponse
from src.main_rag_chain import setup_rag_pipeline, get_rag_response
# We now need the individual core functions for the upload endpoint
from src.core.data_loader import load_document
from src.core.text_chunker import chunk_text
from src.core.vector_store import add_to_vector_store

# --- Global State ---
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    An async context manager for FastAPI's lifespan event.
    """
    print("--- Application startup: Initializing RAG pipeline... ---")
     # We will now manage documents in a dedicated folder.
    # The pipeline will load ALL documents from this folder on startup.
    # --- HIGHLIGHT START ---
    app_state["docs_path"] = "documents"
    os.makedirs(app_state["docs_path"], exist_ok=True)
    
    # For a clean start during development, we can pass a flag
    # For now, we just initialize with whatever is in the folder
    collection, embedding_model = await asyncio.to_thread(setup_rag_pipeline, app_state["docs_path"])
    
    if collection is None or embedding_model is None:
        print("--- ❌ FATAL: RAG pipeline failed to initialize. ---")
        raise RuntimeError("Could not initialize RAG pipeline.")
        
    app_state["rag_collection"] = collection
    app_state["embedding_model"] = embedding_model
    
    print("--- ✅ RAG pipeline initialized successfully. Application is ready. ---")

    yield
    
    print("--- Application shutdown: Cleaning up resources... ---")
    app_state.clear()
    print("--- ✅ Cleanup complete. ---")


# Initialize the FastAPI application with the lifespan manager
app = FastAPI(lifespan=lifespan)

# --- 🛠️ ADD THIS MIDDLEWARE ---
# This is the fix for the CORS issue.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. For production, you'd list specific domains.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.).
    allow_headers=["*"],  # Allows all headers.
)


@app.get("/", summary="Check if the API is running")
def read_root():
    """A simple endpoint to confirm that the API is running."""
    return {"status": "CollegeBot API is running."}


@app.post("/ask", response_model=AskResponse, summary="Ask the chatbot a question")
async def ask_question(request: AskRequest):
    """
    The main endpoint for interacting with the chatbot.
    """
    try:
        collection = app_state.get("rag_collection")
        embedding_model = app_state.get("embedding_model")
        
        if not collection or not embedding_model:
            raise HTTPException(status_code=503, detail="RAG pipeline is not available or still initializing.")
            
        answer = await asyncio.to_thread(get_rag_response, request.query, collection, embedding_model)
        
        return AskResponse(answer=answer)
        
    except Exception as e:
        print(f"--- ❌ An error occurred during the /ask request: {e} ---")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")


@app.post("/upload", summary="Upload a new PDF document to the knowledge base")
async def upload_document(pdf_file: UploadFile = File(...)):
    """
    Handles the upload of a new PDF document.
    - Saves the file to the 'documents' directory.
    - Processes the document (loads, chunks).
    - Adds the new knowledge to the live vector database.
    """
    if pdf_file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are accepted.")

    try:
        # Define the path to save the uploaded file
        file_path = os.path.join(app_state["docs_path"], pdf_file.filename)
        
        # Save the uploaded file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(pdf_file.file, buffer)
        
        print(f"--- New document saved: {file_path} ---")

        # --- Process the new document and add to RAG ---
        collection = app_state.get("rag_collection")
        embedding_model = app_state.get("embedding_model")

        print("--- Processing new document for RAG pipeline... ---")
        document_text = await asyncio.to_thread(load_document, file_path)
        text_chunks = await asyncio.to_thread(chunk_text, document_text)
        
        doc_metadatas = [{
            'source_document_name': pdf_file.filename,
        } for _ in text_chunks]

        await asyncio.to_thread(add_to_vector_store, collection, text_chunks, doc_metadatas, embedding_model)
        
        print(f"--- ✅ Successfully added {pdf_file.filename} to the knowledge base. ---")

        return {"filename": pdf_file.filename, "message": "Document uploaded and processed successfully."}

    except Exception as e:
        print(f"--- ❌ An error occurred during file upload: {e} ---")
        raise HTTPException(status_code=500, detail=f"An error occurred during file processing: {e}")

# To run this application:
# 1. Make sure your llama.cpp server is running in a separate terminal.
# 2. Open another terminal in the project's root directory ('college-ai-assistant/').
# 3. Run the command: uvicorn src.api.main:app --reload

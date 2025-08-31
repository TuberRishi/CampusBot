import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, TextLoader

# --- Load Environment Variables ---
load_dotenv()

# --- Configuration ---
DATA_PATH = "data"
DB_PATH = "faiss_index" # Path to save the FAISS index file
EMBEDDING_MODEL_NAME = "models/text-embedding-004"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

def main():
    """
    Main function to ingest data into a FAISS vector store.
    - Loads documents from the data directory.
    - Splits documents into chunks.
    - Generates embeddings for the chunks via Google's API.
    - Creates a FAISS index and saves it locally.
    """
    print("Starting data ingestion using FAISS...")

    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file.")
        return

    # Load documents
    loader = DirectoryLoader(
        DATA_PATH,
        glob="**/*.txt",
        loader_cls=TextLoader,
        show_progress=True,
        use_multithreading=True
    )
    documents = loader.load()

    if not documents:
        print("No documents found to ingest. Exiting.")
        return

    print(f"Loaded {len(documents)} documents.")

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    texts = text_splitter.split_documents(documents)
    print(f"Split documents into {len(texts)} chunks.")

    # Initialize embeddings client
    print(f"Initializing Google embedding model: {EMBEDDING_MODEL_NAME}...")
    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL_NAME,
        google_api_key=api_key
    )
    print("Google embedding model initialized.")

    # Create FAISS index from documents
    print("Creating FAISS index...")
    db = FAISS.from_documents(texts, embeddings)
    print("FAISS index created successfully.")

    # Save the FAISS index locally
    print(f"Saving FAISS index to: {DB_PATH}...")
    db.save_local(DB_PATH)
    print("FAISS index saved successfully.")

    print("Data ingestion complete.")


if __name__ == "__main__":
    main()

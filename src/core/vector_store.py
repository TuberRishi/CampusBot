import chromadb
import os
import sys
import datetime

# Add the project root to the Python path to allow importing from other 'src' directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import the necessary functions from the previous modules for testing
from src.core.embedding_generator import get_embedding_model
from src.core.data_loader import load_document
from src.core.text_chunker import chunk_text

# --- Database Configuration ---
# Define the path where the persistent database will be stored.
DB_PATH = "db/chroma_db"
# Define a name for the collection within the database.
COLLECTION_NAME = "college_docs"

def get_vector_store_client():
    """
    Initializes and returns a persistent ChromaDB client.
    """
    os.makedirs(DB_PATH, exist_ok=True)
    client = chromadb.PersistentClient(path=DB_PATH)
    return client

def get_or_create_collection(client: chromadb.Client, name: str = COLLECTION_NAME):
    """
    Retrieves a collection from the ChromaDB client, or creates it if it doesn't exist.
    """
     # We NO LONGER delete the collection on startup. This ensures our data persists
    # across server restarts, which is the core of the fix.
    collection = client.get_or_create_collection(name=name)
    print(f"--- Collection '{name}' loaded. Current document count: {collection.count()} ---")
    return collection

def add_to_vector_store(collection: chromadb.Collection, chunks: list[str], metadatas: list[dict], embedding_model):
    """
    Generates embeddings and adds documents and metadata to the collection.
    
    Args:
        collection: The ChromaDB collection to add data to.
        chunks: The list of text chunks (the actual documents).
        metadatas: A list of dictionaries containing metadata for each chunk.
        embedding_model: The embedding model instance to generate vectors.
    """
    # Generate embeddings for the chunks
    embeddings = embedding_model.embed_documents(chunks)
    
    # ChromaDB requires a unique ID for each document.
    count = collection.count()
    ids = [f"id_{count + i}" for i in range(len(chunks))]
    
    collection.add(
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )

def query_vector_store(collection: chromadb.Collection, query_text: str, embedding_model, n_results: int = 4) -> dict:
    """
    Embeds a query and searches the vector store for the most similar documents.
    
    Args:
        collection: The ChromaDB collection to query.
        query_text: The user's text query.
        embedding_model: The embedding model instance to generate the query vector.
        n_results: The number of results to return.
        
    Returns:
        A dictionary containing the query results.
    """
    # Embed the user's query text
    query_embedding = embedding_model.embed_query(query_text)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results

# # --- Testing Block ---
# if __name__ == "__main__":
    
#     # --- 1. Initialization ---
#     print("--- Initializing ChromaDB client and collection... ---")
#     db_client = get_vector_store_client()
#     collection = get_or_create_collection(db_client, name=COLLECTION_NAME)
#     print(f"--- ✅ Client and collection '{collection.name}' ready. Initial count: {collection.count()} ---")

#     print("\n--- Initializing embedding model... ---")
#     embedding_model = get_embedding_model()
    
#     # --- 2. Load and Process Real Document ---
#     # IMPORTANT: Make sure this path is correct for your system.
#     TEST_DOCUMENT_PATH = "C:\\Users\\Tuber\\OneDrive\\Documents\\Tuber Rishi\\College chatbot\\V1\\Structure\\RAG files\\Attention_is_all_you_need.pdf"
    
#     print(f"\n--- Loading and chunking document: '{TEST_DOCUMENT_PATH}' ---")
#     document_text = load_document(TEST_DOCUMENT_PATH)
    
#     if document_text:
#         text_chunks = chunk_text(document_text)
#         print(f"--- ✅ Document loaded and split into {len(text_chunks)} chunks. ---")

#         # Create metadata for each chunk
#         doc_metadatas = [{
#             'source_document_name': os.path.basename(TEST_DOCUMENT_PATH),
#             'ingestion_date': datetime.date.today().isoformat(),
#             'document_type': 'Research Paper'
#         } for _ in text_chunks]

#         # --- 3. Add Data to Vector Store ---
#         print(f"\n--- Adding {len(text_chunks)} chunks to '{collection.name}'... ---")
#         add_to_vector_store(collection, text_chunks, doc_metadatas, embedding_model)
#         print(f"--- ✅ Data added successfully. New count: {collection.count()} ---")

#         # --- 4. Execute Test Queries ---
#         print("\n--- Running test queries against the document... ---")
        
#         test_queries = [
#             "What is a Transformer model?",
#             "What is self-attention?",
#             "What are the main components of the network architecture?",
#             "How does multi-head attention work?"
#         ]

#         for query in test_queries:
#             print(f"\n--- Querying for: '{query}' ---")
#             query_results = query_vector_store(collection, query, embedding_model, n_results=2)
            
#             for i, doc in enumerate(query_results['documents'][0]):
#                 print(f"\n--- Result {i+1} ---")
#                 # ChromaDB returns distance, not similarity. Lower is better.
#                 print(f"Similarity Score (Distance): {query_results['distances'][0][i]:.4f}")
#                 print(f"Document Chunk: '{doc}'")
#                 print("-" * 25)
#     else:
#         print(f"--- ❌ Failed to load the test document: {TEST_DOCUMENT_PATH}. Please check the file path. ---")

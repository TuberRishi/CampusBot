import os
# After
from src.core.data_loader import load_document
from src.core.text_chunker import chunk_text
from src.core.embedding_generator import get_embedding_model
from src.core.vector_store import get_vector_store_client, get_or_create_collection, add_to_vector_store, query_vector_store
from src.core.prompt_builder import build_prompt
from src.core.llm_interface import get_llm_response

def setup_rag_pipeline(document_path: str):
    """
    Sets up the entire RAG pipeline: loads a document, chunks it,
    embeds it, and stores it in a vector database.

    Args:
        document_path: The path to the document to be processed.

    Returns:
        A tuple containing the ChromaDB collection and the embedding model.
    """
    print("--- 1. Initializing RAG Pipeline Setup ---")
    
    # Initialize models and database clients
    embedding_model = get_embedding_model()
    db_client = get_vector_store_client()
    collection = get_or_create_collection(db_client)
    
    # Check if the document is already processed and stored
    # For this simple script, we check if the collection is empty.
    # A more robust check would involve checking metadata.
    if collection.count() > 0:
        print("--- ✅ Collection already contains data. Skipping ingestion. ---")
        return collection, embedding_model

    # Load and process the document
    print(f"--- Loading and chunking document: {document_path} ---")
    document_text = load_document(document_path)
    if not document_text:
        print("--- ❌ Failed to load document. Exiting. ---")
        return None, None
        
    text_chunks = chunk_text(document_text)
    print(f"--- ✅ Document split into {len(text_chunks)} chunks. ---")

    # Create metadata
    doc_metadatas = [{
        'source_document_name': os.path.basename(document_path),
    } for _ in text_chunks]

    # Add to vector store
    print(f"--- Adding {len(text_chunks)} chunks to vector store... ---")
    add_to_vector_store(collection, text_chunks, doc_metadatas, embedding_model)
    print(f"--- ✅ Data ingestion complete. ---")
    
    return collection, embedding_model

def get_rag_response(query: str, collection, embedding_model) -> str:
    """
    Takes a user query and returns a response from the LLM using the RAG pipeline.

    Args:
        query: The user's question.
        collection: The ChromaDB collection object.
        embedding_model: The embedding model object.

    Returns:
        The final response from the LLM.
    """
    print(f"\n--- 2. Processing Query: '{query}' ---")
    
    # 1. Query the vector store to get relevant context
    print("--- Searching for relevant context in vector store... ---")
    search_results = query_vector_store(collection, query, embedding_model, n_results=4)
    
    # 2. Format the retrieved documents into a single context string
    context_parts = []
    for doc, meta in zip(search_results['documents'][0], search_results['metadatas'][0]):
        source = meta.get('source_document_name', 'Unknown Source')
        context_part = f"Source: {source}\nContent: {doc}"
        context_parts.append(context_part)
    
    context = "\n\n---\n\n".join(context_parts)
    
    # 3. Build the prompt with the context and query
    print("--- Building prompt for LLM... ---")
    prompt = build_prompt(context, query)
    
    # 4. Get the response from the LLM
    print("--- Sending prompt to LLM and awaiting response... ---")
    response = get_llm_response(prompt)
    
    return response

# # --- Main Execution Block ---
# if __name__ == "__main__":
#     # IMPORTANT: Make sure this path is correct for your system.
#     PDF_PATH = "C:\\Users\\Tuber\\OneDrive\\Documents\\Tuber Rishi\\College chatbot\\V1\\Structure\\RAG files\\Attention_is_all_you_need.pdf"
    
#     # Setup the pipeline. This will only ingest the document the first time.
#     collection, embedding_model = setup_rag_pipeline(PDF_PATH)
    
#     if collection and embedding_model:
#         print("\n--- ✅ RAG Pipeline is ready. You can now ask questions. ---")
#         print("--- Type 'exit' to quit. ---")
        
#         # Interactive query loop
#         while True:
#             user_query = input("\nPlease enter your question: ")
#             if user_query.lower() == 'exit':
#                 break
            
#             # Get the response
#             final_answer = get_rag_response(user_query, collection, embedding_model)
            
#             # Print the final answer
#             print("\n--- CollegeBot's Answer ---")
#             print(final_answer)
#             print("-" * 30)
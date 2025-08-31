import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def diagnose_embeddings():
    """
    A minimal script to test only the GoogleGenerativeAIEmbeddings client.
    """
    print("--- Starting Embedding Diagnostic ---")

    # 1. Load environment variables
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file.")
        return

    print("API Key found.")

    # 2. Initialize the embedding client
    try:
        print("Initializing GoogleGenerativeAIEmbeddings...")
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=api_key
        )
        print("SUCCESS: Embedding client initialized without error.")
    except Exception as e:
        print(f"FAILURE: Could not initialize embedding client.")
        print(f"Error: {e}")
        return

    # 3. Embed a simple query
    try:
        test_query = "This is a test."
        print(f"Attempting to embed the query: '{test_query}'")
        vector = embeddings.embed_query(test_query)
        print("SUCCESS: Query embedded without error.")
        print(f"Vector length: {len(vector)}")
    except Exception as e:
        print(f"FAILURE: Could not embed query.")
        print(f"Error: {e}")
        return

    print("\n--- Diagnostic Complete: All steps succeeded. ---")
    print("This suggests the Google embedding client is working correctly.")
    print("The 'Bus error' is likely related to another library, such as ChromaDB.")

if __name__ == "__main__":
    diagnose_embeddings()

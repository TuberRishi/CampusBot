# from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
import numpy as np
import torch

# 1. Determine the device to use.
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"--- Using device: {device} ---")
if device == "cpu":
    print("--- WARNING: Running on CPU is slow. For better performance, install PyTorch with CUDA support. ---")

# 2. Define the model name and keyword arguments for the model.
MODEL_NAME = "BAAI/bge-large-en-v1.5"
MODEL_KWARGS = {"device": device}

# Normalizing embeddings is recommended for BGE models to improve similarity search performance.
ENCODE_KWARGS = {'normalize_embeddings': True}

def get_embedding_model():
    """
    Initializes and returns the BGE embedding model from HuggingFace.
    This function centralizes the model loading process.

    Returns:
        An instance of the HuggingFaceBgeEmbeddings model.
    """
    embedding_model = HuggingFaceBgeEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs=MODEL_KWARGS,
        encode_kwargs=ENCODE_KWARGS
    )
    return embedding_model

def generate_embeddings(chunks: list[str], embedding_model) -> list[list[float]]:
    """
    Generates embeddings for a list of text chunks using the provided model.

    Args:
        chunks: A list of text strings (chunks).
        embedding_model: The initialized HuggingFaceBgeEmbeddings model instance.

    Returns:
        A list of lists, where each inner list is a numerical vector (embedding).
    """
    # The embed_documents method efficiently processes a list of texts
    # and returns their corresponding vector representations.
    embeddings = embedding_model.embed_documents(chunks)
    return embeddings

# --- Testing Block ---
# This code runs only when the script is executed directly.
# It's designed to test the embedding generation in isolation.
if __name__ == "__main__":

    print("--- Initializing embedding model... ---")
    print("NOTE: The first time this runs, it will download the model files, which may take some time.")

    # 1. Load the embedding model
    model = get_embedding_model()
    print("\n--- ✅ Model Initialized Successfully. ---")

    # 2. Create a small list of sample text chunks for the test
    sample_chunks_for_testing = [
        "This is a test of the embedding generation process.",
        "Admissions procedures are outlined in the student handbook.",
        "What are the library hours during final exams?"
    ]
    print(f"\n--- Generating embeddings for {len(sample_chunks_for_testing)} sample chunks... ---")

    # 3. Call the function to generate the embeddings
    generated_embeddings = generate_embeddings(sample_chunks_for_testing, model)

    # 4. Verify the output
    print("\n--- ✅ Embeddings Generated Successfully. ---")
    print("\n--- Verification Details ---")

    # Check that we got one vector for each chunk of text
    print(f"Number of text chunks: {len(sample_chunks_for_testing)}")
    print(f"Number of vectors generated: {len(generated_embeddings)}")

    # Check the dimensionality of the vectors
    if generated_embeddings:
        # Convert the first vector to a NumPy array to easily check its properties
        first_vector = np.array(generated_embeddings[0])
        print(f"Dimensionality of vectors: {first_vector.shape[0]}")
        # BGE-large-en-v1.5 model is expected to produce 1024-dimensional vectors
        print(f"Preview of the first vector (first 5 dimensions): {first_vector[:5]}")
    else:
        print("\n--- ❌ Error: No embeddings were generated. ---")
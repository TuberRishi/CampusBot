import os
import sys
from langchain_text_splitters import RecursiveCharacterTextSplitter

# This line adds the project's root directory to the Python path.
# This is necessary to allow this script to import modules from other folders,
# such as the 'data_loader' from the previous step, especially for testing.
# It finds the directory of the current file, goes up two levels ('..', '..') to reach
# the 'college-ai-assistant/' root, and adds it to the list of paths Python searches.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Now that the path is set up, we can import the function from the previous step.
from src.core.data_loader import load_document

# Define chunking parameters based on the project plan 
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

def chunk_text(text: str) -> list[str]:
    """
    Splits a long text into smaller, overlapping chunks.

    Args:
        text: The single string of text to be chunked.

    Returns:
        A list of strings, where each string is a text chunk.
    """
    # Initialize the text splitter from the LangChain library
    # The RecursiveCharacterTextSplitter is effective for maintaining semantic context.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,        # The maximum size of each chunk (in characters) 
        chunk_overlap=CHUNK_OVERLAP,  # The number of characters to overlap between chunks 
        length_function=len,          # The function used to measure the size of a chunk
        is_separator_regex=False,
    )
    
    # Use the splitter to create the chunks from the input text
    chunks = text_splitter.split_text(text)
    
    # Return the list of text chunks
    return chunks

# --- Testing Block ---
# This code will only run when you execute this file directly from the command line.
# Its purpose is to test the 'chunk_text' function in isolation.
if __name__ == "__main__":
    
    # IMPORTANT: Update this path to point to your test PDF file.
    # This should be the same file you used to test the data_loader.py script.
    TEST_DOCUMENT_PATH = "C:\\Users\\Tuber\\OneDrive\\Documents\\Tuber Rishi\\College chatbot\\V1\\Structure\\RAG files\\Attention_is_all_you_need.pdf"
    
    print(f"--- Loading document for chunking test: {TEST_DOCUMENT_PATH} ---")
    
    # 1. Load the document text using the function from the previous step
    full_text = load_document(TEST_DOCUMENT_PATH)

    if full_text:
        print("\n--- ✅ Document loaded. Now chunking text... ---")
        
        # 2. Pass the extracted text to the chunk_text function we want to test
        text_chunks = chunk_text(full_text)
        
        # 3. Print verification information to the console
        print(f"\n--- ✅ Text successfully split into {len(text_chunks)} chunks. ---")
        
        print("\n--- Verifying the first 3 chunks as per the plan: ---")
        for i, chunk in enumerate(text_chunks[:3]):
            print(f"\n--- Chunk {i+1} (Length: {len(chunk)} characters) ---")
            print(f'"{chunk}"')
            print("-" * 40)
            
    else:
        print("\n--- ❌ Failed to load document for chunking test. ---")
        print("Please ensure the file path is correct and the document is readable.")
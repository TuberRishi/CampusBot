import os
from pypdf import PdfReader

def load_document(file_path: str) -> str:
    """
    Extracts text from a PDF document.

    Args:
        file_path: The path to the PDF file.

    Returns:
        A single string containing all the text from the document.
        Returns an empty string if the file is not found or an error occurs.
    """
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found at the specified path: {file_path}")
        return ""
    
    # Check if the file is a PDF
    if not file_path.lower().endswith('.pdf'):
        print(f"Error: File is not a PDF: {file_path}")
        return ""

    try:
        # Initialize a PDF reader object
        reader = PdfReader(file_path)
        
        # Initialize an empty string to store the text
        full_text = ""
        
        # Loop through each page in the PDF
        for page in reader.pages:
            # Extract text from the page and append it to the full_text string
            # Add a newline character for separation between pages
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
            
        return full_text.strip()
    except Exception as e:
        print(f"An error occurred while reading the PDF: {e}")
        return ""

# --- Testing Block ---
# This code will only run when you execute this file directly.
# It allows you to test this module in isolation with your own documents.
if __name__ == "__main__":
    
    # IMPORTANT:
    # 1. Replace the placeholder below with the actual path to YOUR test PDF.
    # 2. On Windows, your path might look like: "C:\\Users\\YourUser\\Documents\\test.pdf"
    # 3. On macOS or Linux, it might look like: "/home/youruser/documents/test.pdf"
    
    TEST_DOCUMENT_PATH = "C:\\Users\\Tuber\\OneDrive\\Documents\\Tuber Rishi\\College chatbot\\V1\\Structure\\RAG files\\Attention_is_all_you_need.pdf"
    
    print(f"--- Loading Document: {TEST_DOCUMENT_PATH} ---")
    
    # Load the document using the function we want to test
    extracted_text = load_document(TEST_DOCUMENT_PATH)

    # Print the results to verify
    if extracted_text:
        print("\n--- ✅ Document Loaded Successfully ---")
        print("\n--- First 500 Characters of Extracted Text ---")
        print(extracted_text[:500] + "...")
    else:
        print("\n--- ❌ Failed to Load Document ---")
        print("Please check the file path and ensure it is a valid PDF.")

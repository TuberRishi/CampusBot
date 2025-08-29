import requests
import json

# --- LLM Server Configuration ---
# This is the endpoint for the local llama.cpp server.
# The project plan specifies using llama.cpp for local development.
LLM_API_URL = "http://localhost:8080/completion"

def get_llm_response(prompt: str) -> str:
    """
    Sends a prompt to the local LLM server and returns the response.

    Args:
        prompt: The fully formatted prompt string to send to the LLM.

    Returns:
        The text response from the LLM. Returns an error message if
        communication fails.
    """
    headers = {"Content-Type": "application/json"}
    
    # The data payload must match what the llama.cpp server expects.
    # 'prompt' is the key for the input text.
    # 'n_predict' controls the maximum length of the response.
    # 'temperature' controls creativity. 0.0 is deterministic.
    data = {
        "prompt": prompt,
        "n_predict": 512,
        "temperature": 0.0, 
        "stop": ["\nUser:", "User:", "Instructions:"] # Helps prevent the model from hallucinating a conversation
    }

    try:
        # Make the POST request to the LLM server
        response = requests.post(LLM_API_URL, headers=headers, data=json.dumps(data))
        
        # Raise an exception if the server returned an error status code
        response.raise_for_status()
        
        # Parse the JSON response and extract the generated text
        response_data = response.json()
        
        # The key for the response content in llama.cpp server is 'content'
        return response_data.get('content', '').strip()

    except requests.exceptions.RequestException as e:
        error_message = f"Error communicating with LLM server: {e}"
        print(error_message)
        return error_message
    except json.JSONDecodeError:
        error_message = "Error: Could not decode JSON response from LLM server."
        print(error_message)
        return error_message

# --- Testing Block ---
if __name__ == "__main__":
    
    print("--- Testing LLM Interface ---")
    print(f"--- Attempting to connect to LLM server at: {LLM_API_URL} ---")
    
    # This is a simple prompt to test basic connectivity and response generation.
    # In the full RAG chain, this prompt will be much more complex.
    test_prompt = "Who are you?"

    print(f"\n--- Sending Test Prompt --- \n{test_prompt}")
    
    # Call the function we want to test
    llm_response = get_llm_response(test_prompt)

    print("\n--- Received LLM Response ---")
    
    # Print the result
    if llm_response:
        print(llm_response)
    else:
        print("--- ❌ Failed to get a response from the LLM. ---")
        print("--- Ensure the llama.cpp server is running and accessible at the configured URL. ---")
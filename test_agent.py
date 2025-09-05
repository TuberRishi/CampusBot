import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def run_test():
    """
    Sends a series of test queries to the chatbot API and prints the responses.
    """
    chat_url = f"{BASE_URL}/chat"

    queries = [
        {"query": "Hello, who are you?", "language": "en"},
        {"query": "When is the deadline for semester fee payment?", "language": "en"},
        {"query": "When is Tech Fest 2025?", "language": "en"},
        {"query": "What is the capital of France?", "language": "en"}
    ]

    print("--- Starting Agent Integration Tests ---")

    for i, payload in enumerate(queries):
        print(f"\n--- Test {i+1}: Query: '{payload['query']}' ---")
        try:
            response = requests.post(chat_url, json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes

            response_data = response.json()
            print("Status Code: 200 OK")
            print("Response JSON:")
            print(json.dumps(response_data, indent=2))

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            if e.response:
                print("Error Response:")
                try:
                    print(json.dumps(e.response.json(), indent=2))
                except json.JSONDecodeError:
                    print(e.response.text)

    print("\n--- Agent Integration Tests Complete ---")

if __name__ == "__main__":
    run_test()

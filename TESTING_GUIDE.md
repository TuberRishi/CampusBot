# CampusBot v2.0: Testing Guide

This guide provides instructions on how to test the CampusBot application to ensure all its components are working correctly. It covers both automated tests and a manual testing plan.

---

## Part 1: Automated Testing

The project includes a suite of automated tests that verify the core logic of the agent, including routing, translation, and memory.

### Prerequisites

1.  **Complete the Setup**: You must follow the `SETUP_GUIDE.md` to install all dependencies and set up the environment.
2.  **Valid Google API Key**: The test suite will fail if you do not have a valid `GEMINI_API_KEY` in your `.env` file, as it needs to test the RAG and translation features.
3.  **Data and DB**: Ensure you have run `python src/database_setup.py` and `python src/ingest.py` at least once.

### How to Run the Tests

1.  Open a **Command Prompt** or **PowerShell** in the project's root directory (`CampusBot`).
2.  Activate your Python virtual environment:
    ```bash
    .venv\Scripts\activate
    ```
3.  Run the tests using `pytest`:
    ```bash
    PYTHONPATH=. pytest src/tests/test_agent_v2.py
    ```
    -   **`PYTHONPATH=.`** is important. It tells Python to include the project's root directory in its path, allowing the tests to import the `src` modules correctly.

### Expected Output

If all tests pass, you will see a summary indicating success (e.g., `======== 6 passed in ...s ========`). This confirms that the agent's core logic is working as expected with the default Google Gemini configuration.

**Note**: These tests are designed to run against the default Google LLM configuration. They may produce different results if run after you have switched the code to use Ollama.

---

## Part 2: Manual Testing Plan

Manual testing is crucial to ensure the end-to-end functionality is working as you expect with your **local Ollama setup**.

### Prerequisites

-   You have successfully followed the **Ollama-based setup** in the `SETUP_GUIDE.md`.
-   The backend server is running (`uvicorn src.main:app --reload`).
-   Ollama is running with the `llama3` model.
-   You have the `frontend/index.html` page open in your browser.

### Test Cases

Here are a series of questions to ask the chatbot. For each question, check that you get the expected type of answer.

#### Test Case 1: Testing the RAG Tool

This tests the chatbot's ability to retrieve information from the local `.txt` files in the `data/` folder.

-   **Sample Question**: `"What is the fee payment deadline?"`
-   **What to Look For**:
    -   The answer should be based on the content of `dummy_fees_circular.txt`.
    -   It should mention the deadline (e.g., "October 31st").
    -   The backend console should print `---ROUTE: RAG---`.

#### Test Case 2: Testing the SQL Tool

This tests the chatbot's ability to query the `college_events.db` database for real-time information.

-   **Sample Question**: `"Are there any events on October 10th, 2025?"`
-   **What to Look For**:
    -   The answer should mention "Tech Fest" and "CodeClash Coding Competition".
    -   The backend console should print `---ROUTE: SQL---`.
    -   The console should also show the generated SQL query (e.g., `---DEBUG: Generated SQL Query: SELECT ...`).

#### Test Case 3: Testing the External Help Tool

This tests the chatbot's ability to provide contact information when a user needs to speak to a person.

-   **Sample Question**: `"Who should I contact about my exam scores?"`
-   **What to Look For**:
    -   The answer should provide the contact details for the "Examinations Department".
    -   It should include the email `exams@examplecollege.edu`.
    -   The backend console should print `---ROUTE: External Help---`.

#### Test Case 4: Testing the General QA Tool

This tests the chatbot's ability to handle conversational or general knowledge questions that don't fit other tools.

-   **Sample Question**: `"Hello, who are you?"`
-   **What to Look For**:
    -   The answer should be a friendly, conversational response.
    -   It should introduce itself as "CampusBot".
    -   The backend console should print `---ROUTE: General---`.

#### Test Case 5: Testing Conversational Memory

This tests if the chatbot can remember the context of the conversation to answer follow-up questions.

1.  **First Question**: `"Are there any workshops or guest lectures scheduled?"`
    -   The bot should respond by mentioning the "Guest Lecture on AI".
2.  **Follow-up Question**: `"When is it?"`
    -   **What to Look For**:
        -   The chatbot should understand that "it" refers to the guest lecture from the previous turn.
        -   The answer should correctly state the date and time (e.g., "September 25th at 3:00 PM").
        -   The backend console will likely route this to SQL or RAG after the query is refined using the conversation history.

---

If the chatbot responds correctly to all these manual tests, you can be confident that your local setup is fully functional.

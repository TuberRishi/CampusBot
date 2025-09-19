# CampusBot v2.0: Step-by-Step Setup Guide (Windows & Ollama)

This guide provides detailed instructions to set up and run the CampusBot project on a Windows machine, with a focus on using a local LLM via Ollama.

## ⚠️ Important Prerequisite: Google API Key

Even when using a local LLM like Ollama for generating chat responses, this project **still requires a Google Gemini API key** for two critical features:

1.  **Document Embeddings (RAG)**: The script that reads your local documents (`ingest.py`) uses Google's models to understand and index the text. Without this, the chatbot cannot answer questions about your documents.
2.  **Language Translation**: The chatbot's ability to understand and respond in multiple languages is powered by the Google Translate API.

**To get your API key:**
1.  Go to the [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Sign in with your Google account.
3.  Click "**Create API key**".
4.  Copy the generated key. You will need it in **Step 3**.

---

## Setup Instructions

### Step 1: Install a Git Client

If you don't already have Git installed, download and install it from [git-scm.com](https://git-scm.com/download/win). This will help you download the project files.

### Step 2: Download the Project

1.  Open the **Command Prompt** or **PowerShell** (you can find it in the Start Menu).
2.  Navigate to the directory where you want to store the project. For example, to use your Documents folder:
    ```bash
    cd %USERPROFILE%\Documents
    ```
3.  Clone the repository (assuming the project is hosted on GitHub). You will need to replace `[repository_url]` with the actual URL.
    ```bash
    git clone [repository_url] CampusBot
    cd CampusBot
    ```

### Step 3: Set Up Environment Variables

You need to provide the Google API key to the application.

1.  In the project's root directory (`CampusBot`), find the file named `.env.example`.
2.  Make a copy of this file and rename it to `.env`.
3.  Open the new `.env` file in a text editor (like Notepad).
4.  It will look like this:
    ```
    GEMINI_API_KEY="YOUR_API_KEY_HERE"
    ```
5.  Replace `"YOUR_API_KEY_HERE"` with the actual API key you got from the Google AI Studio.
6.  Save and close the file.

### Step 4: Install Python

If you don't have Python, install it from the [official Python website](https://www.python.org/downloads/).
-   Download the latest stable version (e.g., Python 3.10+).
-   **Important**: During installation, make sure to check the box that says "**Add Python to PATH**".

### Step 5: Install Project Dependencies

1.  Open a new **Command Prompt** or **PowerShell** window and navigate to the `CampusBot` directory again.
2.  It's highly recommended to use a Python virtual environment to avoid conflicts with other projects. Create one by running:
    ```bash
    python -m venv .venv
    ```
3.  Activate the virtual environment:
    ```bash
    .venv\Scripts\activate
    ```
    Your command prompt should now show `(.venv)` at the beginning of the line.
4.  Install all the required Python libraries from `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

### Step 6: Configure the Code to Use Ollama

You need to make small edits to two files to switch the LLM from Google Gemini to your local Ollama model.

1.  **Open `src/agent_v2/router.py`**:
    -   Find these lines:
        ```python
        # Google Gemini LLM (requires API key)
        api_key = os.getenv("GEMINI_API_KEY")
        router_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0, google_api_key=api_key)

        # Ollama LLM (local, no API key required)
        # router_llm = ChatOllama(model="llama3", temperature=0)
        ```
    -   Modify them to look like this (comment out the Google LLM and uncomment the Ollama LLM):
        ```python
        # Google Gemini LLM (requires API key)
        # api_key = os.getenv("GEMINI_API_KEY")
        # router_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0, google_api_key=api_key)

        # Ollama LLM (local, no API key required)
        router_llm = ChatOllama(model="llama3", temperature=0)
        ```

2.  **Open `src/agent_v2/chains.py`**:
    -   Find these lines near the top of the file:
        ```python
        # Google Gemini LLM (requires API key)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not found in .env file. LLM will likely fail.")
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0, google_api_key=api_key)

        # Ollama LLM (local, no API key required)
        # llm = ChatOllama(model="llama3", temperature=0)
        ```
    -   Modify them to look like this:
        ```python
        # Google Gemini LLM (requires API key)
        # api_key = os.getenv("GEMINI_API_KEY")
        # if not api_key:
        #     print("Warning: GEMINI_API_KEY not found in .env file. LLM will likely fail.")
        # llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0, google_api_key=api_key)

        # Ollama LLM (local, no API key required)
        llm = ChatOllama(model="llama3", temperature=0)
        ```

### Step 7: Prepare the Data and Database

These commands prepare the chatbot's knowledge sources.

1.  **Set up the events database**:
    ```bash
    python src/database_setup.py
    ```
2.  **Process local documents for RAG**:
    -   Place any `.txt` files you want the chatbot to know about into the `data/` directory.
    -   Run the ingestion script (this is the step that uses your Google API key):
    ```bash
    python src/ingest.py
    ```

### Step 8: Run the Application

1.  **Install and run Ollama**:
    -   Download and install Ollama for Windows from [ollama.com](https://ollama.com/).
    -   Once installed, open a new Command Prompt and pull the `llama3` model:
        ```bash
        ollama pull llama3
        ```
    -   Ollama will run in the background. You can check that it's working by running `ollama list`.

2.  **Start the FastAPI Backend Server**:
    -   In your project's command prompt (with the virtual environment still active), run:
        ```bash
        uvicorn src.main:app --reload
        ```
    -   Wait until you see a message indicating the server is running, like `Uvicorn running on http://127.0.0.1:8000`.

3.  **Open the Frontend**:
    -   Navigate to the `frontend` folder in your file explorer.
    -   Double-click the `index.html` file to open it in your web browser.

You should now be able to chat with CampusBot!

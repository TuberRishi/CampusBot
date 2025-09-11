# CampusBot - Multilingual College Chatbot

A multilingual conversational AI assistant designed to help college students with routine queries.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API key OR a running Ollama instance

### Installation

1.  **Clone and navigate to project**
    ```bash
    cd ChatBot_25104_V2
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables**
    If you are using the Google Gemini API, create a `.env` file in the project root with your key:
    ```env
    GEMINI_API_KEY=your_gemini_api_key_here
    ```

4.  **Set up the database and vector store**
    ```bash
    python src/database_setup.py
    python src/ingest.py
    ```

5.  **Start the API server**
    ```bash
    uvicorn src.main:app --reload
    ```

## 🔧 Configuration

### Using a Local LLM (Ollama)

To run the chatbot with a local model using Ollama (and avoid Google API costs/rate limits), follow these steps:

1.  **Install and run Ollama:** Make sure you have Ollama installed on your system and have pulled a model. For example:
    ```bash
    ollama run llama3
    ```

2.  **Modify the code:** In `src/agent_v2/chains.py` and `src/agent_v2/router.py`, you can switch between the Google and Ollama models. The files are set up like this:

    ```python
    # --- LLM Initialization ---

    # To switch to a local Ollama model, comment out the Google LLM
    # and uncomment the Ollama LLM.

    # Google Gemini LLM (requires API key)
    api_key = os.getenv("GEMINI_API_KEY")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0, google_api_key=api_key)

    # Ollama LLM (local, no API key required)
    # llm = ChatOllama(model="llama3", temperature=0)
    ```
    Simply swap which `llm = ...` line is commented out to change the model.

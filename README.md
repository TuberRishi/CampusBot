# CampusBot - Multilingual College Chatbot v2.0

A multilingual, stateful, multi-tool conversational AI assistant designed to help college students with routine queries. Built with FastAPI, LangGraph, and Google's Gemini AI.

## 🎯 Problem Statement

Campus offices handle hundreds of repetitive queries daily - fee deadlines, scholarship forms, timetable changes - often from students more comfortable in Hindi or other regional languages. This creates long queues and communication gaps. CampusBot aims to provide 24/7 multilingual support by understanding institutional documents and providing accurate, contextual responses.

## ✨ Current Features

### ✅ Implemented
- **Advanced Agentic Architecture**: A robust, stateful agent built with LangGraph that can intelligently route user queries.
- **Multi-turn Conversation Memory**: The agent maintains conversation history, allowing it to understand context and answer follow-up questions.
- **Full Multilingual Translation Pipeline**: The agent can detect the user's language, process the query in English, and translate the final answer back into one of 6 supported languages.
- **Multi-tool Capability**: The agent can dynamically choose the best tool for a given query:
    - **RAG**: For questions about college documents (fees, deadlines, etc.).
    - **SQL**: For questions about real-time data like college events.
    - **External Help**: A fallback to provide users with the correct human contact information.
    - **General QA**: For all other conversational queries.
- **REST API Backend**: FastAPI server with CORS support for easy web integration.
- **SQLite Events DB**: A sample events database is fully integrated with the SQL tool.
- **Modular Codebase**: The new agent is built with a highly modular structure in the `src/agent_v2` directory for easy maintenance and future expansion.
- **Local LLM Support (Optional)**: Includes commented-out code and instructions to easily switch to a local LLM using Ollama.

### ❌ Not Yet Implemented
- **Conversation Logging**: No persistent interaction logs for review and improvement.
- **Enhanced Document Support**: Only `.txt` files are currently supported for ingestion; PDF support is a key next step.
- **Messaging Platform Integration**: No direct integration with WhatsApp, Telegram, etc.
- **Production Security**: No authentication or rate limiting on the API.

## 🏗️ Architecture

The new architecture is built around a central LangGraph agent that manages state and routes tasks to the appropriate tool chain.

```
+--------------------------+
|      User (Query, Lang)  |
+--------------------------+
             |
             v
+--------------------------+      +--------------------------+
|   FastAPI /chat Endpoint |----->|      Session Store       |
| (Manages Chat History)   |      | (In-Memory Dictionary)   |
+--------------------------+      +--------------------------+
             |
             v
+-------------------------------------------------------------+
|                     LangGraph Agent                         |
|                                                             |
|  +---------------------+   +--------------------------+     |
|  | detect_language     |-->| refine_query (w/history) |     |
|  +---------------------+   +--------------------------+     |
|                                      |                      |
|                                      v                      |
|                            +------------------+             |
|                            |   route_query    |             |
|                            +------------------+             |
|                                      |                      |
|          +---------------------------+----------------+     |
|          |             |             |                |     |
|          v             v             v                v     |
|  +-----------+  +----------+  +-------------+  +-------------+
|  | RAG Chain |  | SQL Chain|  | Help Chain  |  |General Chain|
|  +-----------+  +----------+  +-------------+  +-------------+
|          |             |             |                |     |
|          +---------------------------+----------------+     |
|                                      |                      |
|                                      v                      |
|                        +--------------------------+         |
|                        | after_tool (conditional) |         |
|                        +--------------------------+         |
|                                | (if not 'en')              |
|                                v                            |
|                       +----------------------+              |
|                       | translate_final_answer|             |
|                       +----------------------+              |
|                                |                            |
+--------------------------------|----------------------------+
                                 v
+-------------------------------------------------------------+
|                      Final Answer                           |
+-------------------------------------------------------------+
```

## 📁 Project Structure

```
ChatBot_25104_V2/
├── src/
│   ├── main.py                 # FastAPI server, endpoints, and session management
│   ├── agent.py                # Original agent (deprecated)
│   ├── agent_v2/               # New LangGraph agent
│   │   ├── __init__.py
│   │   ├── chains.py           # All processing chains (RAG, SQL, etc.)
│   │   ├── graph.py            # Assembles and compiles the LangGraph agent
│   │   ├── router.py           # The core routing logic
│   │   └── state.py            # Defines the agent's state object
│   ├── ingest.py               # Document ingestion and FAISS indexing
│   ├── database_setup.py       # SQLite events database setup
│   └── ...
├── frontend/
│   └── ...
├── data/
│   └── ...
├── college_events.db           # SQLite events database
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API key OR a running Ollama instance

### Installation
1.  **Install dependencies**: `pip install -r requirements.txt`
2.  **Set up environment variables**: If using Google, create a `.env` file with `GEMINI_API_KEY=your_key`.
3.  **Set up the database and vector store**:
    ```bash
    python src/database_setup.py
    python src/ingest.py
    ```
4.  **Start the API server**: `uvicorn src.main:app --reload`
5.  **Open the frontend**: Open `frontend/index.html` in your browser.

## 🔧 Configuration

### Using a Local LLM (Ollama)
To run with a local model using Ollama:
1.  Ensure Ollama is running (e.g., `ollama run llama3`).
2.  In `src/agent_v2/chains.py` and `src/agent_v2/router.py`, comment out the `ChatGoogleGenerativeAI` lines and uncomment the `ChatOllama` lines.

## 🧪 Testing
To run the new test suite:
```bash
PYTHONPATH=. pytest src/tests/test_agent_v2.py
```

## 🎯 Next Steps (Priority Order)

- [ ] **Phase 3: Logging & Monitoring**: Add conversation logging to a database and create a simple admin dashboard for review.
- [ ] **Phase 4: Enhanced Intelligence**: Add support for ingesting PDF documents in addition to `.txt` files.
- [ ] **Phase 5: Platform Integration**: Integrate the chatbot with Telegram or WhatsApp.
- [ ] **Phase 6: Production Readiness**: Implement API authentication, rate limiting, and containerize the application with Docker.

---

**Last Updated**: September 2025
**Version**: 2.0.0
**Status**: Phase 2 Complete

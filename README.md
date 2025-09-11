# CampusBot - Multilingual College Chatbot

A multilingual conversational AI assistant designed to help college students with routine queries about fees, deadlines, academic calendars, and campus events. Built with FastAPI, LangChain, and Google's Gemini AI.

## 🎯 Problem Statement

Campus offices handle hundreds of repetitive queries daily - fee deadlines, scholarship forms, timetable changes - often from students more comfortable in Hindi or other regional languages. This creates long queues and communication gaps. CampusBot aims to provide 24/7 multilingual support by understanding institutional documents and providing accurate, contextual responses.

## ✨ Current Features

### ✅ Implemented
- **REST API Backend**: FastAPI server with CORS support for web integration
- **RAG-based Knowledge**: Retrieval-Augmented Generation using FAISS vector store
- **Document Ingestion**: Processes `.txt` files from `data/` directory
- **Similarity Threshold**: Guards against irrelevant responses using L2 distance
- **Department Fallback**: Keyword-based routing to appropriate departments
- **Web Interface**: Clean, responsive chat UI
- **SQLite Events DB**: Sample events database (ready for integration)
- **Modular Architecture**: Separated concerns for maintainability

### 🚧 Partially Implemented
- **Multilingual Support**: API accepts language parameter but translation not implemented
- **SQL Tools**: Database query tools created but not integrated with agent

### ❌ Not Yet Implemented
- **Full Translation Pipeline**: No inbound/outbound translation
- **Multi-turn Context**: No conversation memory
- **Intent Recognition**: No explicit intent classification
- **Conversation Logging**: No persistent interaction logs
- **Messaging Platform Integration**: No WhatsApp/Telegram support
- **PDF Support**: Only `.txt` files supported
- **Production Security**: No authentication or rate limiting

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI        │    │   LangChain     │
│   (HTML/JS)     │◄──►│   Backend        │◄──►│   Agent         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Department     │    │   FAISS Vector  │
                       │   Fallback       │    │   Store         │
                       └──────────────────┘    └─────────────────┘
                                                        │
                                                ┌─────────────────┐
                                                │   SQLite        │
                                                │   Events DB     │
                                                └─────────────────┘
```

## 📁 Project Structure

```
ChatBot_25104_V2/
├── src/
│   ├── main.py                 # FastAPI server and endpoints
│   ├── agent.py                # LangChain agent with RAG tools
│   ├── ingest.py               # Document ingestion and FAISS indexing
│   ├── database_setup.py       # SQLite events database setup
│   ├── diag_embed.py           # Embedding diagnostics
│   ├── department_mapping.json # Department contact information
│   └── tools/
│       └── sql_tool.py         # SQL database tools (unused)
├── frontend/
│   ├── index.html              # Chat interface
│   ├── script.js               # Frontend logic
│   └── style.css               # Styling
├── data/
│   ├── dummy_academic_calendar.txt
│   └── dummy_fees_circular.txt
├── faiss_index/                # Generated FAISS vector store
│   ├── index.faiss
│   └── index.pkl
├── college_events.db           # SQLite events database
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API key

### Installation

1. **Clone and navigate to project**
   ```bash
   cd ChatBot_25104_V2
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Set up the database**
   ```bash
   python src/database_setup.py
   ```

5. **Ingest documents and create vector store**
   ```bash
   python src/ingest.py
   ```

6. **Start the API server**
   ```bash
   uvicorn src.main:app --reload
   ```

7. **Open the frontend**
   Open `frontend/index.html` in your browser

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY`: Required. Your Google Gemini API key

### Key Settings (in `src/agent.py`)
- `DISTANCE_THRESHOLD = 0.7`: L2 distance threshold for similarity matching
- `CHUNK_SIZE = 512`: Document chunk size for processing
- `CHUNK_OVERLAP = 50`: Overlap between chunks

### Department Mapping
Edit `src/department_mapping.json` to customize department contacts and keywords.

## 📄 API Endpoints

### POST `/chat`
Main chat endpoint.

**Request:**
```json
{
  "query": "When is the fee payment deadline?",
  "language": "en"
}
```

**Response:**
```json
{
  "answer": "The fee payment deadline is...",
  "source": "agent"
}
```

## 🧪 Testing

### Test the agent directly
```bash
python src/agent.py
```

### Test embeddings
```bash
python src/diag_embed.py
```

### Test database tools
```bash
python src/tools/sql_tool.py
```

## 📝 Current Limitations

1. **No Translation**: Language parameter accepted but not processed
2. **No Context Memory**: Each query is independent
3. **Basic Fallback**: Simple keyword matching only
4. **No Logging**: No persistent conversation logs
5. **Limited File Types**: Only `.txt` files supported
6. **No Production Security**: CORS open, no authentication

## 🎯 Next Steps (Priority Order)

### Phase 1: Core Multilingual Support
- [ ] Implement Google Translate integration
- [ ] Add conversation memory/session management
- [ ] Support 5+ regional languages (Hindi, Marathi, Bengali, Tamil, Telugu)

### Phase 2: Enhanced Intelligence
- [ ] Integrate SQL tools for event queries
- [ ] Implement intent recognition
- [ ] Improve fallback with fuzzy matching

### Phase 3: Logging & Monitoring
- [ ] Add conversation logging to database
- [ ] Create admin dashboard for review
- [ ] Implement feedback collection

### Phase 4: Platform Integration
- [ ] Telegram bot integration
- [ ] WhatsApp integration
- [ ] Mobile app considerations

### Phase 5: Production Readiness
- [ ] PDF/document support
- [ ] Authentication and rate limiting
- [ ] Docker containerization
- [ ] CI/CD pipeline

## 📄 License

This project is developed for educational purposes as part of the Smart India Hackathon 2024.

## 🆘 Troubleshooting

### Common Issues

1. **"Agent is not initialized"**
   - Ensure you've run `python src/ingest.py` to create the FAISS index
   - Check that `faiss_index/` directory exists with `index.faiss` and `index.pkl`

2. **"GEMINI_API_KEY not found"**
   - Create `.env` file with your API key
   - Ensure `.env` is in the project root directory

3. **"Database file not found"**
   - Run `python src/database_setup.py` to create the events database

4. **CORS errors in browser**
   - Ensure API server is running on `http://localhost:8000`
   - Open browser console to check for specific errors

### Debug Mode
Run the server with debug logging:
```bash
uvicorn src.main:app --reload --log-level debug
```

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Status**: Development Phase

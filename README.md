# 📚 Document-Grounded RAG Assistant

A local/cloud Retrieval-Augmented Generation (RAG) assistant for asking questions about PDF documents.

The system allows users to upload PDF files, index them into a vector database, retrieve relevant document chunks, and generate grounded answers using either a local Ollama model or the OpenAI API.

---

## ✨ Features

- PDF document upload
- PDF text extraction
- Text cleaning
- Document chunking
- Sentence-transformer embeddings
- Persistent ChromaDB vector storage
- Semantic similarity search
- Retrieval-Augmented Generation (RAG)
- Source filename and page references
- Local LLM support with Ollama
- Cloud LLM support with OpenAI
- Runtime provider switching
- No-answer behavior for unrelated questions
- Streamlit graphical interface
- Document listing
- Document re-indexing
- Document deletion
- Automated evaluation suite

---

## 🏗️ Architecture

The application follows a modular RAG architecture:

```text
PDF Documents
      │
      ▼
PDF Loader
      │
      ▼
Text Cleaner
      │
      ▼
Chunker
      │
      ▼
Embedding Model
      │
      ▼
ChromaDB Vector Store
      │
      ▼
Semantic Retrieval
      │
      ▼
Relevant Context
      │
      ▼
RAG Pipeline
      │
      ├───────────────┐
      ▼               ▼
Ollama Provider   OpenAI Provider
(Local LLM)       (Cloud LLM)
      │               │
      └───────┬───────┘
              ▼
       Grounded Answer
              │
              ▼
      Sources + Page Numbers

```
The same RAGPipeline is used for both LLM providers.

---


📁 Project Structure
```
document-rag-assistant/
│
├── app.py
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── sample_documents/
│
├── evaluation/
│   ├── __init__.py
│   ├── questions.json
│   ├── results.json
│   └── run_evaluation.py
│
├── src/
│   ├── __init__.py
│   │
│   ├── document_management/
│   │   └── __init__.py
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── pdf_loader.py
│   │   ├── cleaner.py
│   │   └── chunker.py
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── ollama_provider.py
│   │   └── openai_provider.py
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   └── pipeline.py
│   │
│   └── retrieval/
│       ├── __init__.py
│       ├── embedder.py
│       ├── indexer.py
│       ├── retriever.py
│       └── vector_store.py
│
├── chroma_db/
├── data/
├── docs/
├── tests/
└── config/
```
---

⚙️ Requirements

* Python 3.12+
* Ollama
* Internet connection for OpenAI API usage
* macOS, Linux, or Windows

---

🚀 Installation

Clone the repository:
```
git clone <your-repository-url>
cd document-rag-assistant
```
Create a virtual environment:
```
python -m venv .venv
```
Activate it.

macOS / Linux
```
source .venv/bin/activate
```
Windows
```
.venv\Scripts\activate
```

Install dependencies:
```
pip install -r requirements.txt
```

---

🔐 Environment Variables
Create a .env file in the project root.

You can start from:
```
.env.example
```
Example:
```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5.6-luna

```

Important:

* Never commit .env
* Never share API keys publicly
* .env is ignored by Git

---

🧠 Ollama Setup

Install Ollama from the official Ollama website.

Then download the local model:
```
ollama pull qwen2.5:3b
```

Test it:
```
ollama run qwen2.5:3b "Say hello in Romanian."
```
If Ollama is not already running:
```
ollama serve
```

---

☁️ OpenAI Setup
Create an OpenAI Platform account and generate an API key.

Store the key in:
```
.env
```
Example:
```
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5.6-luna
```

The application loads the key using python-dotenv.

---

▶️ Running the Application

Activate the virtual environment:
```
source .venv/bin/activate
```
Start the Streamlit interface:
```
streamlit run app.py
```
Then open:
```
http://localhost:8501
```
---

🖥️ Using the Application

1. Select an LLM provider

Choose:
```
Ollama (Local)
```
or:
```
OpenAI (Cloud)
```
The RAG pipeline remains unchanged when switching providers.

2. Upload a PDF

Use the document uploader in the sidebar.

3. Index the document

Click:
```
Index Documents
```
The application will:
```
PDF
↓
Extract text
↓
Clean text
↓
Create chunks
↓
Generate embeddings
↓
Store vectors in ChromaDB
```
4. Ask a question

Example:
```
Ce este programarea orientata pe obiecte?
```
The system retrieves relevant chunks and generates an answer based only on the indexed documentation.

5. Review sources

Each grounded answer can display:

* filename
* page number
* similarity score
---



















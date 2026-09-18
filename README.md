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

The same RAGPipeline is used for both LLM providers.
```









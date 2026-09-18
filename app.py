from pathlib import Path

import streamlit as st

from src.retrieval.indexer import index_pdf
from src.rag.pipeline import RAGPipeline
from src.llm.ollama_provider import OllamaProvider
from src.llm.openai_provider import OpenAIProvider


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Document RAG Assistant",
    page_icon="📚",
    layout="wide",
)


# --------------------------------------------------
# Project paths
# --------------------------------------------------

SAMPLE_DOCUMENTS_DIR = Path("sample_documents")
SAMPLE_DOCUMENTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# --------------------------------------------------
# Session state
# --------------------------------------------------

if "last_result" not in st.session_state:
    st.session_state.last_result = None


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("📚 Document-Grounded RAG Assistant")

st.caption(
    "Upload PDF documents, index them, and ask grounded "
    "questions with source references."
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.header("⚙️ Settings")

    provider_name = st.selectbox(
        "LLM Provider",
        [
            "Ollama (Local)",
            "OpenAI (Cloud)",
        ],
    )

    st.write("Selected provider:")
    st.code(provider_name)

    st.divider()

    st.subheader("📄 Documents")

    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        st.success(
            f"{len(uploaded_files)} PDF file(s) selected."
        )

    index_button = st.button(
        "Index Documents",
        type="primary",
        use_container_width=True,
    )


# --------------------------------------------------
# Index uploaded PDFs
# --------------------------------------------------

if index_button:

    if not uploaded_files:

        st.warning(
            "Please upload at least one PDF before indexing."
        )

    else:

        st.subheader("📥 Indexing")

        indexing_results = []

        for uploaded_file in uploaded_files:

            destination = (
                SAMPLE_DOCUMENTS_DIR
                / uploaded_file.name
            )

            with open(destination, "wb") as file:
                file.write(
                    uploaded_file.getbuffer()
                )

            with st.spinner(
                f"Indexing {uploaded_file.name}..."
            ):

                try:

                    result = index_pdf(
                        str(destination)
                    )

                    indexing_results.append(
                        result
                    )

                    st.success(
                        f"{uploaded_file.name} "
                        "indexed successfully."
                    )

                except Exception as exc:

                    st.error(
                        f"Could not index "
                        f"{uploaded_file.name}: "
                        f"{exc}"
                    )

        if indexing_results:

            st.subheader(
                "✅ Indexed Documents"
            )

            for result in indexing_results:

                st.write(
                    f"**File:** "
                    f"{result.get('filename', 'Unknown')}"
                )

                st.write(
                    f"Pages: "
                    f"{result.get('pages', 'N/A')}"
                )

                st.write(
                    f"Chunks: "
                    f"{result.get('chunks', 'N/A')}"
                )

                st.write(
                    f"Vector store count: "
                    f"{result.get('vector_store_count', 'N/A')}"
                )

                st.divider()


# --------------------------------------------------
# Question area
# --------------------------------------------------

st.subheader("💬 Ask a Question")

question = st.text_area(
    "Question",
    placeholder=(
        "Example: "
        "Ce este programarea orientata pe obiecte?"
    ),
    height=120,
)

ask_button = st.button(
    "Ask",
    type="primary",
)


# --------------------------------------------------
# Ask RAG pipeline
# --------------------------------------------------

if ask_button:

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        try:

            # Choose LLM provider
            if provider_name == "Ollama (Local)":

                llm_provider = OllamaProvider()

            else:

                llm_provider = OpenAIProvider()

            # Same RAG pipeline for both providers
            rag = RAGPipeline(
                llm_provider,
                top_k=3,
                min_similarity=0.65,
            )

            with st.spinner(
                "Searching documents and generating answer..."
            ):

                result = rag.answer(
                    question
                )

            st.session_state.last_result = result

        except Exception as exc:

            st.session_state.last_result = None

            st.error(
                f"Could not generate answer: {exc}"
            )


# --------------------------------------------------
# Answer / sources area
# --------------------------------------------------

st.divider()

answer_column, source_column = st.columns(
    [2, 1]
)


with answer_column:

    st.subheader("🤖 Answer")

    if st.session_state.last_result:

        answer = (
            st.session_state
            .last_result
            .get(
                "answer",
                "No answer returned.",
            )
        )

        st.success(answer)

    else:

        st.info(
            "Your grounded answer "
            "will appear here."
        )


with source_column:

    st.subheader("📚 Sources")

    if st.session_state.last_result:

        sources = (
            st.session_state
            .last_result
            .get(
                "sources",
                [],
            )
        )

        if not sources:

            st.warning(
                "No supporting sources were found."
            )

        else:

            for number, source in enumerate(
                sources,
                start=1,
            ):

                filename = source.get(
                    "filename",
                    "Unknown",
                )

                page = source.get(
                    "page",
                    "N/A",
                )

                similarity = source.get(
                    "similarity",
                )

                st.markdown(
                    f"**Source {number}**"
                )

                st.write(
                    f"📄 {filename}"
                )

                st.write(
                    f"📍 Page: {page}"
                )

                if similarity is not None:

                    st.write(
                        "🎯 Similarity: "
                        f"{similarity:.3f}"
                    )

                st.divider()

    else:

        st.info(
            "Source documents and page "
            "numbers will appear here."
        )
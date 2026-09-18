from pathlib import Path

import streamlit as st

from src.retrieval.indexer import index_pdf
from src.retrieval.vector_store import VectorStore
from src.rag.pipeline import RAGPipeline
from src.llm.ollama_provider import OllamaProvider
from src.llm.openai_provider import OpenAIProvider


# ==================================================
# Page configuration
# ==================================================

st.set_page_config(
    page_title="Document RAG Assistant",
    page_icon="📚",
    layout="wide",
)


# ==================================================
# Project paths
# ==================================================

SAMPLE_DOCUMENTS_DIR = Path("sample_documents")

SAMPLE_DOCUMENTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ==================================================
# Session state
# ==================================================

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "notification" not in st.session_state:
    st.session_state.notification = None


# ==================================================
# Header
# ==================================================

st.title("📚 Document-Grounded RAG Assistant")

st.caption(
    "Upload PDF documents, index them, and ask grounded "
    "questions with source references."
)


# ==================================================
# Notification after rerun
# ==================================================

if st.session_state.notification:

    notification_type, message = (
        st.session_state.notification
    )

    if notification_type == "success":
        st.success(message)

    elif notification_type == "error":
        st.error(message)

    elif notification_type == "warning":
        st.warning(message)

    st.session_state.notification = None


# ==================================================
# Sidebar
# ==================================================

with st.sidebar:

    # ----------------------------------------------
    # LLM settings
    # ----------------------------------------------

    st.header("⚙️ Settings")

    provider_name = st.selectbox(
        "LLM Provider",
        [
            "Ollama (Local)",
            "OpenAI (Cloud)",
        ],
    )

    st.write("Selected provider:")

    st.code(
        provider_name
    )

    st.divider()

    # ----------------------------------------------
    # Upload documents
    # ----------------------------------------------

    st.subheader("📄 Documents")

    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if uploaded_files:

        st.success(
            f"{len(uploaded_files)} "
            "PDF file(s) selected."
        )

    index_button = st.button(
        "Index Documents",
        type="primary",
        use_container_width=True,
    )

    st.divider()

    # ----------------------------------------------
    # Existing documents
    # ----------------------------------------------

    st.subheader("📚 Existing Documents")

    existing_documents = sorted(
        SAMPLE_DOCUMENTS_DIR.glob(
            "*.pdf"
        )
    )

    if not existing_documents:

        st.info(
            "No PDF documents found."
        )

    else:

        for document_path in existing_documents:

            filename = document_path.name

            st.markdown(
                f"**📄 {filename}**"
            )

            button_col_1, button_col_2 = (
                st.columns(2)
            )

            # --------------------------------------
            # Re-index button
            # --------------------------------------

            with button_col_1:

                reindex_clicked = st.button(
                    "🔄 Re-index",
                    key=f"reindex_{filename}",
                    use_container_width=True,
                )

            # --------------------------------------
            # Delete button
            # --------------------------------------

            with button_col_2:

                delete_clicked = st.button(
                    "🗑️ Delete",
                    key=f"delete_{filename}",
                    use_container_width=True,
                )

            # --------------------------------------
            # Re-index action
            # --------------------------------------

            if reindex_clicked:

                try:

                    vector_store = VectorStore()

                    # Remove previous chunks
                    vector_store.delete_document_by_filename(
                        filename
                    )

                    # Index the document again
                    with st.spinner(
                        f"Re-indexing {filename}..."
                    ):

                        result = index_pdf(
                            str(document_path)
                        )

                    st.session_state.last_result = None

                    st.session_state.notification = (
                        "success",
                        (
                            f"{filename} was "
                            "re-indexed successfully. "
                            f"Pages: "
                            f"{result.get('pages', 'N/A')}, "
                            f"Chunks: "
                            f"{result.get('chunks', 'N/A')}."
                        ),
                    )

                    st.rerun()

                except Exception as exc:

                    st.error(
                        f"Could not re-index "
                        f"{filename}: {exc}"
                    )

            # --------------------------------------
            # Delete action
            # --------------------------------------

            if delete_clicked:

                try:

                    vector_store = VectorStore()

                    # Delete chunks from ChromaDB
                    removed_document_ids = (
                        vector_store
                        .delete_document_by_filename(
                            filename
                        )
                    )

                    # Delete physical PDF file
                    if document_path.exists():

                        document_path.unlink()

                    # Remove old answer from UI
                    st.session_state.last_result = None

                    st.session_state.notification = (
                        "success",
                        (
                            f"{filename} was deleted. "
                            f"Removed indexed document "
                            f"entries: "
                            f"{removed_document_ids}."
                        ),
                    )

                    st.rerun()

                except Exception as exc:

                    st.error(
                        f"Could not delete "
                        f"{filename}: {exc}"
                    )

            st.divider()


# ==================================================
# Index uploaded PDFs
# ==================================================

if index_button:

    if not uploaded_files:

        st.warning(
            "Please upload at least one PDF "
            "before indexing."
        )

    else:

        st.subheader("📥 Indexing")

        indexing_results = []

        for uploaded_file in uploaded_files:

            destination = (
                SAMPLE_DOCUMENTS_DIR
                / uploaded_file.name
            )

            # Save uploaded PDF
            with open(
                destination,
                "wb",
            ) as file:

                file.write(
                    uploaded_file.getbuffer()
                )

            try:

                # ----------------------------------
                # Remove previous index if same
                # filename already exists in DB
                # ----------------------------------

                vector_store = VectorStore()

                vector_store.delete_document_by_filename(
                    uploaded_file.name
                )

                # ----------------------------------
                # Create new index
                # ----------------------------------

                with st.spinner(
                    f"Indexing "
                    f"{uploaded_file.name}..."
                ):

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

        # ------------------------------------------
        # Indexing metadata
        # ------------------------------------------

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


# ==================================================
# Question area
# ==================================================

st.subheader(
    "💬 Ask a Question"
)

question = st.text_area(
    "Question",
    placeholder=(
        "Example: "
        "Ce este programarea orientata "
        "pe obiecte?"
    ),
    height=120,
)

ask_button = st.button(
    "Ask",
    type="primary",
)


# ==================================================
# Ask RAG pipeline
# ==================================================

if ask_button:

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        try:

            # --------------------------------------
            # Choose LLM provider
            # --------------------------------------

            if provider_name == "Ollama (Local)":

                llm_provider = (
                    OllamaProvider()
                )

            else:

                llm_provider = (
                    OpenAIProvider()
                )

            # --------------------------------------
            # Same RAG pipeline for both providers
            # --------------------------------------

            rag = RAGPipeline(
                llm_provider,
                top_k=3,
                min_similarity=0.65,
            )

            with st.spinner(
                "Searching documents "
                "and generating answer..."
            ):

                result = rag.answer(
                    question
                )

            st.session_state.last_result = (
                result
            )

        except Exception as exc:

            st.session_state.last_result = None

            st.error(
                f"Could not generate "
                f"answer: {exc}"
            )


# ==================================================
# Answer and sources
# ==================================================

st.divider()

answer_column, source_column = (
    st.columns(
        [2, 1]
    )
)


# ==================================================
# Answer
# ==================================================

with answer_column:

    st.subheader(
        "🤖 Answer"
    )

    if st.session_state.last_result:

        answer = (
            st.session_state
            .last_result
            .get(
                "answer",
                "No answer returned.",
            )
        )

        st.success(
            answer
        )

    else:

        st.info(
            "Your grounded answer "
            "will appear here."
        )


# ==================================================
# Sources
# ==================================================

with source_column:

    st.subheader(
        "📚 Sources"
    )

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
                "No supporting sources "
                "were found."
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
# ui.py
import streamlit as st
import os
import tempfile
from datetime import datetime
from pathlib import Path
from backend import MultilingualBackend

st.set_page_config(page_title="Multilingual Document Q&A (Groq)", layout="wide")
st.title("📄 Multilingual Document Q&A System ")


backend = MultilingualBackend()

SUPPORTED_LANGS = [
    ("English", "en"), ("Hindi", "hi"), ("Gujarati", "gu"),
    ("Marathi", "mr"), ("Tamil", "ta"), ("Bengali", "bn"),
    ("Kannada", "kn"), ("Telugu", "te")
]

st.sidebar.header("UI Settings")
user_lang_name, user_lang_code = st.sidebar.selectbox("Select your language", SUPPORTED_LANGS, index=0, format_func=lambda x: x[0])

st.header("1) Upload PDF (10–15 pages recommended)")
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_file.write(uploaded_file.getbuffer())
    save_path = temp_file.name

    try:
        pdf_doc = backend.load_pdf_document(save_path)
    except Exception as e:
        st.error(f"Failed to process PDF: {e}")
        st.stop()

    st.subheader("Uploaded PDF")
    st.write(f"**Filename:** {uploaded_file.name}")
    preview = " ".join(pdf_doc.full_text.split())[:300]
    st.markdown("**Extracted text preview (first 300 chars):**")
    st.text_area("Preview", value=preview, height=120)

    st.markdown("---")
    st.header("2) Ask a question (any language)")
    user_question = st.text_area("Your question", placeholder="Ask anything about the uploaded PDF...")
    ask_button = st.button("Ask")

    if ask_button and user_question:
        with st.spinner("Detecting language, translating, retrieving context, and answering..."):
            result = backend.answer_question(pdf_doc, user_question, user_lang_code)

        st.markdown("### Output")
        st.write(f"**Detected language:** {result.get('detected_language')}")
        st.write(f"**Translated -> English (question):** {result.get('question_english')}")
        st.write("**Answer (English):**")
        st.info(result.get("answer_english"))
        st.write(f"**Final Answer (translated to {user_lang_name}):**")
        st.success(result.get("answer_translated"))

        st.markdown("**Context snippets used (top matches):**")
        for i, sc in enumerate(result.get("used_chunks", []), start=1):
            st.markdown(f"- **Snippet {i}** (score: {sc['score']:.4f})")
            st.write(sc["snippet"][:500] + ("..." if len(sc["snippet"]) > 500 else ""))

else:
    st.info("Upload a PDF to begin.")

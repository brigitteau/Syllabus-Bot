import hashlib
import io
import streamlit as st
import docx
import pdfplumber

from src.parse import parse_pdf, parse_text
from src.chunk import chunk_text
from src.embed import embed_chunks, embed_question
from src.retrieve import retrieve
from src.llm import generate_answer


st.set_page_config(page_title="Syllabus Q&A", page_icon="📚")
st.title("Syllabus Q&A")

@st.cache_data(show_spinner=False)
def extract_text(file_bytes, filename):
    """Pull plain text out of a PDF, DOCX, or TXT upload."""
    name = filename.lower()

    if name.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")

    if name.endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)

    if name.endswith(".docx"):
        d = docx.Document(io.BytesIO(file_bytes))
        parts = [p.text for p in d.paragraphs]
        # Tables (like grading breakdowns) are stored separately in DOCX files
        for table in d.tables:
            for row in table.rows:
                parts.append(" | ".join(cell.text.strip() for cell in row.cells))
        return "\n".join(parts)

    return ""

# Chat history lives in session_state because Streamlit reruns this
# whole script on every interaction.
if "messages" not in st.session_state:
    st.session_state.messages = []

def show_sources(sources):
    with st.expander("Sources used"):
        for s in sources:
            st.caption(f"{s['section']} | page {s['pages']} | similarity {s['score']:.2f}")
            st.text(s["text"])

# Sidebar: syllabus upload or paste
with st.sidebar:
    uploaded = st.file_uploader("Upload a syllabus", type=["pdf", "docx", "txt"])
    pasted = st.text_area("Or paste your syllabus text", height=250)

syllabus_text = ""
source_name = ""

if uploaded is not None:
    source_name = uploaded.name
    try:
        syllabus_text = extract_text(uploaded.getvalue(), uploaded.name)
    except Exception as e:
        st.error(f"Couldn't read {uploaded.name}: {e}")
        st.stop()
    if not syllabus_text.strip():
        st.warning(
            "No text found in that file. If it's a scanned PDF (an image of "
            "pages), it can't be read yet. Try pasting the text instead."
        )
        st.stop()
elif pasted.strip():
    source_name = "pasted text"
    syllabus_text = pasted

if not syllabus_text:
    st.info("Upload a syllabus or paste its text in the sidebar to get started.")
    st.stop()

# Build the index only when the syllabus changes. Streamlit reruns this script
# on every message, so without this check it would re-embed the syllabus each time.
source_bytes = uploaded.getvalue() if uploaded is not None else syllabus_text.encode("utf-8")
file_id = hashlib.sha256(source_name.encode("utf-8") + b"\0" + source_bytes).hexdigest()

if st.session_state.get("file_id") != file_id:
    try:
        with st.spinner("Reading and indexing your syllabus..."):
            if uploaded is not None and uploaded.name.lower().endswith(".pdf"):
                pages = parse_pdf(io.BytesIO(source_bytes))               # parse.py: file -> page records
            else:
                pages = parse_text(syllabus_text)
            chunks = chunk_text(pages)                                    # chunk.py: pages -> chunks
            if not chunks:
                raise ValueError("No text found. If this is a scanned PDF, it needs OCR first.")
            st.session_state.chunks = chunks
            st.session_state.embeddings = embed_chunks(chunks)            # embed.py: chunks -> vectors
            st.session_state.file_id = file_id
            st.session_state.messages = []
    except Exception as e:
        st.error(f"Could not process this file: {e}")
        st.stop()

st.success(f"Loaded: {source_name}")

# Show past messages
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("sources"):
            show_sources(m["sources"])

# Chat box
if question := st.chat_input("Ask about the syllabus"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        sources = []
        try:
            with st.spinner("Searching the syllabus..."):
                results = retrieve(                                       # retrieve.py: question -> top chunks
                    question,
                    st.session_state.chunks,
                    embed_question=embed_question,                        # embed.py: question -> vector
                    chunk_embeddings=st.session_state.embeddings,
                )
                top = [st.session_state.chunks[r["index"]] for r in results]
                for c, r in zip(top, results):
                    sources.append({
                        "section": c["section"] or "General",
                        "pages": ", ".join(str(p) for p in c["pages"]),
                        "score": r["score"],
                        "text": c["text"],
                    })
                # llm.py joins plain strings, so give it text with the section and page attached
                context = [f"[{s['section']} | page {s['pages']}]\n{s['text']}" for s in sources]
                answer = generate_answer(question, context) or "I couldn't generate an answer. Please try again."
        except Exception as e:
            answer, sources = f"Sorry, something went wrong: {e}", []
        st.markdown(answer)
        if sources:
            show_sources(sources)

    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
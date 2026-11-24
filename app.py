import hashlib
import io
from collections import Counter

import streamlit as st
import docx

from src.parse import parse_pdf, parse_text
from src.chunk import chunk_text
from src.embed import embed_chunks, embed_question
from src.retrieve import retrieve
from src.llm import generate_answer


st.set_page_config(page_title="Syllabus Q&A", page_icon="📚")
st.title("Syllabus Q&A")

def extract_text(file_bytes, filename):
    """Pull plain text out of a DOCX or TXT upload."""
    name = filename.lower()

    if name.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")

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
            st.caption(
                f"{s['filename']} | {s['section']} | page {s['pages']} | similarity {s['score']:.2f}"
            )
            st.text(s["text"])

# Sidebar: syllabus upload or paste
with st.sidebar:
    uploaded = st.file_uploader(
        "Upload syllabi", type=["pdf", "docx", "txt"], accept_multiple_files=True
    )
    pasted = st.text_area("Or paste your syllabus text", height=250)

if uploaded:
    inputs = [(file.name, file.getvalue()) for file in uploaded]
elif pasted.strip():
    inputs = [("pasted text", pasted.encode("utf-8"))]
else:
    inputs = []

# Reuse indexes for unchanged files and discard indexes for removed files.
files = {(name, hashlib.sha256(data).digest()): data for name, data in inputs}
file_ids = frozenset(files)
if st.session_state.get("file_ids") != file_ids:
    st.session_state.file_ids = file_ids
    st.session_state.messages = []
    st.session_state.pop("syllabus_scope", None)

previous_indexes = st.session_state.get("syllabus_indexes", {})
indexes = {}
for file_id, data in files.items():
    if file_id in previous_indexes:
        indexes[file_id] = previous_indexes[file_id]
        continue

    filename, _ = file_id
    try:
        with st.spinner(f"Reading and indexing {filename}..."):
            if filename.lower().endswith(".pdf"):
                pages = parse_pdf(io.BytesIO(data))
            elif uploaded:
                pages = parse_text(extract_text(data, filename))
            else:
                pages = parse_text(pasted)
            chunks = chunk_text(pages)
            if not chunks:
                st.warning(f"No readable text in {filename}. Scanned PDFs need OCR.")
                continue
            indexes[file_id] = (chunks, embed_chunks(chunks))
    except Exception as e:
        st.error(f"Could not process {filename}: {e}")

st.session_state.syllabus_indexes = indexes
if not files:
    st.info("Upload syllabi or paste syllabus text in the sidebar to get started.")
    st.stop()
if not indexes:
    st.button("Retry indexing")
    st.stop()

name_counts = Counter(filename for filename, _ in indexes)
name_numbers = Counter()
source_labels = {}
for file_id in indexes:
    filename, _ = file_id
    name_numbers[filename] += 1
    source_labels[file_id] = (
        f"{filename} ({name_numbers[filename]})" if name_counts[filename] > 1 else filename
    )

st.success(f"Loaded: {', '.join(source_labels.values())}")
scope = None
if len(indexes) > 1:
    scope = st.sidebar.selectbox(
        "Search in",
        [None, *indexes],
        format_func=lambda file_id: "All syllabi" if file_id is None else source_labels[file_id],
        key="syllabus_scope",
    )

# Show past messages
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("sources"):
            show_sources(m["sources"])

# Chat box
if question := st.chat_input("Ask about your syllabi"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        sources = []
        try:
            with st.spinner("Searching your syllabi..."):
                question_vector = embed_question(question.strip())
                # Search each selected syllabus so comparisons get evidence from every file.
                for file_id in indexes if scope is None else [scope]:
                    chunks, embeddings = indexes[file_id]
                    results = retrieve(
                        question,
                        chunks,
                        embed_question=lambda _: question_vector,
                        chunk_embeddings=embeddings,
                    )
                    for result in results:
                        chunk = chunks[result["index"]]
                        sources.append({
                            "filename": source_labels[file_id],
                            "section": chunk["section"] or "General",
                            "pages": ", ".join(str(page) for page in chunk["pages"]),
                            "score": result["score"],
                            "text": chunk["text"],
                        })
                context = [
                    f"[{s['filename']} | {s['section']} | page {s['pages']}]\n{s['text']}"
                    for s in sources
                ]
                answer = generate_answer(question, context) or "I couldn't generate an answer. Please try again."
        except Exception as e:
            answer, sources = f"Sorry, something went wrong: {e}", []
        st.markdown(answer)
        if sources:
            show_sources(sources)

    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})

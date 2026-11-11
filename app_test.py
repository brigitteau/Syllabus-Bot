import io

import docx
import pdfplumber
import streamlit as st

from llm import generate_answer

st.set_page_config(page_title="Syllabus Q&A (test)", page_icon="📚")
st.title("Syllabus Q&A (test)")


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

# Sidebar: upload OR paste
with st.sidebar:
    uploaded = st.file_uploader("Upload a syllabus", type=["pdf", "docx", "txt"])
    pasted = st.text_area("Or paste your syllabus text", height=250)

# Work out the syllabus text from whichever source was given
syllabus_text, source_name = None, None

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

# Start a fresh chat when the syllabus changes
source_key = (source_name, len(syllabus_text))
if st.session_state.get("source_key") != source_key:
    st.session_state.source_key = source_key
    st.session_state.messages = []

st.success(f"Loaded: {source_name} ({len(syllabus_text):,} characters)")
with st.expander("Preview extracted text"):
    st.text(syllabus_text[:2000])

# TODO: replace with the team's pipeline once it's merged:
#   chunks = chunk_text(syllabus_text)        # Isani
#   vectors = embed_chunks(chunks)            # embed.py
#   top_chunks = retrieve(question, ...)      # Andrew
# For now, the whole syllabus is sent to Gemini as one chunk.
chunks = [syllabus_text]

# Show past messages
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Chat box
if question := st.chat_input("Ask about the syllabus"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = generate_answer(question, chunks)
        st.markdown(answer)
        with st.expander("Sources"):
            st.write(chunks)

    st.session_state.messages.append({"role": "assistant", "content": answer})
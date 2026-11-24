import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
    --cream: #FFFDF8;
    --paper: #FBEBD6;
    --peach: #F6D2AE;
    --orange: #E07B39;
    --ink: #3A2E26;
    --muted: #8A7563;
    --line: #E9D5BD;
}

html, body, [data-testid="stApp"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--ink);
}

[data-testid="stApp"] {
    background: var(--cream);
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stMainBlockContainer"] {
    padding-top: 1.2rem;
    max-width: 820px;
}

/* ---------- browser title bar ---------- */
.browser-bar {
    position: sticky;
    top: 0;
    z-index: 50;
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px 16px;
    margin-bottom: 1.6rem;
    background: var(--paper);
    border: 1.5px solid var(--line);
    border-radius: 14px;
    box-shadow: 0 2px 0 var(--line);
}
.browser-dots { display: flex; gap: 7px; }
.browser-dots span {
    width: 12px; height: 12px; border-radius: 50%;
    border: 1px solid rgba(58, 46, 38, 0.25);
}
.browser-dots span:nth-child(1) { background: #E8836B; }
.browser-dots span:nth-child(2) { background: #EDBE5B; }
.browser-dots span:nth-child(3) { background: #A9BF8E; }
.browser-address {
    flex: 1;
    background: var(--cream);
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 5px 14px;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: var(--muted);
}
.browser-title {
    font-family: 'Fraunces', serif;
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--ink);
    white-space: nowrap;
}

/* ---------- hero ---------- */
.hero { text-align: center; margin: 0.5rem 0 1.4rem; }
.hero-badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--orange);
    border: 1px solid var(--peach);
    background: #FFF4E8;
    border-radius: 999px;
    padding: 3px 12px;
}
.hero h1 {
    font-family: 'Fraunces', serif !important;
    font-weight: 600 !important;
    font-size: 2.6rem !important;
    color: var(--ink) !important;
    margin: 0.5rem 0 0.2rem !important;
    padding: 0 !important;
}
.hero p { color: var(--muted); margin: 0; }

/* ---------- sidebar = "uploads" panel ---------- */
[data-testid="stSidebar"] {
    background: var(--paper);
    border-right: 1.5px solid var(--line);
}
.sidebar-heading {
    font-family: 'Fraunces', serif;
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0 0 0.2rem;
}
.sidebar-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: var(--muted);
    margin-bottom: 1rem;
}
[data-testid="stSidebar"] label p {
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    text-transform: lowercase;
    color: var(--muted);
}
[data-testid="stFileUploaderDropzone"],
[data-testid="stSidebar"] textarea {
    background: var(--cream) !important;
    border: 1.5px dashed var(--peach) !important;
    border-radius: 12px !important;
}

/* ---------- status boxes ---------- */
[data-testid="stAlert"],
[data-testid="stAlertContainer"] {
    background: #FFF4E8 !important;
    border-radius: 12px !important;
}
[data-testid="stAlertContainer"] {
    border: 1px solid var(--peach) !important;
}
[data-testid="stAlert"] * {
    color: var(--ink) !important;
}

[data-testid="stMarkdownContainer"] a {
    color: var(--orange) !important;
    text-decoration-color: var(--peach) !important;
}

/* ---------- chat messages ---------- */
[data-testid="stChatMessage"] {
    background: var(--cream);
    border: 1.5px solid var(--line);
    border-radius: 16px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.8rem;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: #FFF1E2;
    border-color: var(--peach);
}
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] {
    border-radius: 10px;
}
[data-testid="stChatMessageAvatarUser"] { background: var(--orange); }
[data-testid="stChatMessageAvatarAssistant"] { background: var(--ink); }
[data-testid="stExpander"] details {
    border: 1px dashed var(--line);
    border-radius: 10px;
    background: #FFFAF2;
}

/* ---------- chat input (glowing search bar) ---------- */
[data-testid="stBottom"] > div { background: var(--cream); }
[data-testid="stChatInput"] {
    border: 1.5px solid var(--orange) !important;
    border-radius: 14px !important;
    background: var(--cream) !important;
    box-shadow: 0 0 0 4px rgba(224, 123, 57, 0.12), 0 6px 18px rgba(224, 123, 57, 0.15);
}
[data-testid="stChatInput"] textarea {
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stChatInputSubmitButton"] {
    background: var(--orange) !important;
    color: white !important;
    border-radius: 10px !important;
}
</style>
"""


def apply_style():
    st.markdown(CSS, unsafe_allow_html=True)


def browser_bar(title="Syllabus Q and A", address="syllabus.qa/ask"):
    st.markdown(
        f"""
        <div class="browser-bar">
            <div class="browser-dots"><span></span><span></span><span></span></div>
            <div class="browser-address">{address}</div>
            <div class="browser-title">{title}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero():
    st.markdown(
        """
        <div class="hero">
            <span class="hero-badge">your syllabus, answered</span>
            <h1>Syllabus Q and A</h1>
            <p>Upload a syllabus and ask anything: deadlines, grading, office hours.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_heading():
    st.markdown(
        '<div class="sidebar-heading">uploads</div>'
        '<div class="sidebar-sub">pdf · docx · txt</div>',
        unsafe_allow_html=True,
    )

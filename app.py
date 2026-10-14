
import os
from pathlib import Path

import requests
import streamlit as st

# -------------------- CONFIGURATION --------------------

st.set_page_config(
    page_title="SINGULARITY AI | QUNIT",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).parent
LOGO_PATH = BASE_DIR / "singularity_logo.png"

SYSTEM_PROMPT = """
You are SINGULARITY AI, created by QUNIT.
Be helpful, accurate, friendly, creative, and clear.
Explain difficult concepts in simple language.
Use headings and examples when useful.
Be honest when you are uncertain.
Never claim to have capabilities you do not have.
"""

# -------------------- COSMIC DESIGN --------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg: #03040b;
    --panel: #090c19;
    --blue: #19baff;
    --purple: #8b5cf6;
    --text: #edf4ff;
    --muted: #8c9ab7;
}

.stApp {
    background:
        radial-gradient(ellipse at 50% 0%, #11173a 0%, transparent 42%),
        radial-gradient(ellipse at 100% 65%, #140c2d 0%, transparent 35%),
        var(--bg);
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

[data-testid="stHeader"] {
    background: rgba(3, 4, 11, 0.75);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080b19, #05060d);
    border-right: 1px solid #20294a;
}

[data-testid="stSidebar"] * {
    color: var(--text);
}

h1, h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    letter-spacing: 1.5px;
}

.hero {
    text-align: center;
    padding: 25px 0 18px 0;
}

.hero img {
    width: min(100%, 430px);
    max-height: 330px;
    object-fit: contain;
    filter: drop-shadow(0 0 24px rgba(39, 130, 255, 0.16));
}

.hero-title {
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(27px, 4vw, 45px);
    font-weight: 700;
    letter-spacing: 5px;
    margin-top: 8px;
    background: linear-gradient(90deg, #f4f8ff, #8bdcff, #9c75ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    color: #a8c9f8;
    font-size: 11px;
    letter-spacing: 5px;
    margin-top: 8px;
}

.status-pill {
    display: inline-block;
    padding: 7px 13px;
    border: 1px solid #1d547a;
    border-radius: 30px;
    color: #80dcff;
    background: rgba(14, 73, 110, 0.15);
    font-size: 12px;
    margin: 12px 0 20px;
}

div[data-testid="stChatMessage"] {
    background: rgba(10, 15, 33, 0.78);
    border: 1px solid #1a2545;
    border-radius: 16px;
    padding: 14px;
    margin-bottom: 12px;
}

.stChatInput textarea {
    background: #090d1c !important;
    color: white !important;
}

.stChatInput {
    border-color: #25365e !important;
}

.stButton > button {
    background: linear-gradient(110deg, #10264a, #251346);
    color: #edf4ff;
    border: 1px solid #31558e;
    border-radius: 12px;
    transition: 0.2s ease;
}

.stButton > button:hover {
    border-color: #30c9ff;
    box-shadow: 0 0 18px rgba(34, 180, 255, 0.22);
    color: white;
}

hr {
    border-color: #20294a;
}

footer {
    visibility: hidden;
}

#MainMenu {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# -------------------- SETTINGS --------------------

def get_secret(name, default=""):
    try:
        return str(st.secrets.get(name, default))
    except Exception:
        return os.getenv(name, default)


API_KEY = get_secret("OPENROUTER_API_KEY").strip()
MODEL = get_secret("OPENROUTER_MODEL", "openrouter/free").strip()

# -------------------- SIDEBAR --------------------

with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)

    st.markdown("## SINGULARITY AI")
    st.caption("BY QUNIT · BEYOND THE KNOWN")
    st.divider()

    st.markdown("### SYSTEM STATUS")

    if API_KEY:
        st.success("Cloud key configured")
    else:
        st.error("Cloud key not configured")

    st.caption(f"Model: {MODEL}")
    st.caption("Engine: OpenRouter")

    st.divider()

    if st.button("＋  NEW CONVERSATION", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("### ABOUT")
    st.caption(
        "An independent AI project by QUNIT, "
        "built to explore ideas beyond the known."
    )

    st.divider()
    st.caption("SINGULARITY AI · QUNIT")

# -------------------- CHAT STATE --------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------- HEADER --------------------

st.markdown('<div class="hero">', unsafe_allow_html=True)

if LOGO_PATH.exists():
    st.image(str(LOGO_PATH), use_container_width=False, width=430)

st.markdown(
    '<div class="hero-title">SINGULARITY AI</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero-subtitle">BY QUNIT · BEYOND THE KNOWN</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="status-pill">✦ INTELLIGENCE WITHOUT BORDERS</div>',
    unsafe_allow_html=True,
)
st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("### What shall we explore?")

    suggestions = [
        "Explain black holes simply",
        "Give me a creative invention idea",
        "Help me solve a difficult problem",
    ]

    cols = st.columns(3)
    for i, suggestion in enumerate(suggestions):
        with cols[i]:
            if st.button(suggestion, use_container_width=True):
                st.session_state.pending_prompt = suggestion
                st.rerun()

# -------------------- API REQUEST --------------------

def ask_openrouter(messages):
    if not API_KEY:
        return (
            "Your OpenRouter API key is missing. Add "
            "`OPENROUTER_API_KEY` in your Streamlit app's "
            "Secrets settings, then restart or redeploy the app."
        )

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages,
        ],
        "temperature": 0.7,
        "max_tokens": 700,
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=90,
        )

        if response.status_code == 401:
            return "The API key was rejected. Check your Streamlit Secrets."
        if response.status_code == 402:
            return "The provider reports insufficient credits or account balance."
        if response.status_code == 403:
            return "The provider denied access to this model or request."
        if response.status_code == 404:
            return "The selected model was not found. Check OPENROUTER_MODEL."
        if response.status_code == 429:
            return "The model is busy or rate-limited. Please try again shortly."

        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]

    except requests.Timeout:
        return "The AI took too long to respond. Please try again."
    except requests.RequestException:
        return "I couldn't reach the AI service. Check your connection and try again."
    except (KeyError, IndexError, ValueError):
        return "The AI service returned an unexpected response. Please try again."

# -------------------- DISPLAY CHAT --------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask SINGULARITY AI anything...")

if "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Connecting to the singularity..."):
            answer = ask_openrouter(st.session_state.messages)
        st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

st.markdown("---")
st.caption("SINGULARITY AI · CREATED BY QUNIT")

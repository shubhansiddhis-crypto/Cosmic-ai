
import os
from pathlib import Path

import requests
import streamlit as st

# =====================================================
# SINGULARITY AI | QUNIT
# =====================================================

BASE_DIR = Path(__file__).parent
LOGO_PATH = BASE_DIR / "singularity_logo.png"

st.set_page_config(
    page_title="SINGULARITY | QUNIT",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- CONFIG ----------------

def get_secret(name, default=""):
    try:
        return str(st.secrets.get(name, default))
    except Exception:
        return os.getenv(name, default)


API_KEY = get_secret("OPENROUTER_API_KEY").strip()
MODEL = get_secret("OPENROUTER_MODEL", "openrouter/free").strip()

SYSTEM_PROMPT = """
You are SINGULARITY AI, an AI assistant created by QUNIT.
Be helpful, accurate, creative, friendly, and clear.
Explain difficult topics simply and use examples when helpful.
Be honest about uncertainty and never invent capabilities.
"""

# ---------------- COSMIC UI ----------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg: #05060b;
    --panel: #0a0d17;
    --line: #1b2237;
    --blue: #61caff;
    --purple: #a78bfa;
    --white: #f0f4ff;
    --muted: #8791ad;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at 50% -18%, rgba(38, 71, 155, .23), transparent 50%),
        radial-gradient(ellipse at 95% 65%, rgba(100, 40, 180, .10), transparent 32%),
        var(--bg);
    color: var(--white);
}

[data-testid="stHeader"] {
    background: rgba(5, 6, 11, .7);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #090c16, #06070d);
    border-right: 1px solid var(--line);
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}

[data-testid="stSidebar"] * {
    color: var(--white);
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -.6px;
}

.block-container {
    max-width: 1050px;
    padding-top: 2rem;
    padding-bottom: 7rem;
}

.brand-mark {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 12px;
    letter-spacing: 4px;
    color: #aab8dc;
    margin-bottom: 10px;
}

.brand-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(30px, 4.6vw, 49px);
    line-height: 1.15;
    font-weight: 600;
    letter-spacing: -2px;
    background: linear-gradient(100deg, #f6f8ff 5%, #a7dfff 52%, #b9a1ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.brand-subtitle {
    color: #8d9ab8;
    font-size: 12px;
    letter-spacing: 3px;
    margin-top: 13px;
}

.hero {
    text-align: center;
    padding: 16px 0 25px;
}

.hero img {
    max-width: 100%;
    object-fit: contain;
}

.hero-logo {
    width: 235px;
    max-width: 80%;
    margin: 0 auto 8px;
    filter: drop-shadow(0 0 24px rgba(46, 145, 255, .18));
}

.eyebrow {
    color: var(--blue);
    font-size: 10px;
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.intro {
    color: #9ba7c4;
    font-size: 14px;
    line-height: 1.7;
    max-width: 510px;
    margin: 12px auto 24px;
}

div[data-testid="stChatMessage"] {
    background: rgba(12, 16, 29, .78);
    border: 1px solid #202842;
    border-radius: 18px;
    padding: 15px 18px;
    margin: 12px 0;
    animation: reveal .25s ease-out;
}

div[data-testid="stChatMessage"] p {
    line-height: 1.75;
}

@keyframes reveal {
    from { opacity: .35; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
}

[data-testid="stChatInput"] {
    border: 1px solid #303a5c !important;
    border-radius: 18px !important;
    background: #0b0e19 !important;
    box-shadow: 0 0 25px rgba(35, 94, 180, .08);
}

[data-testid="stChatInput"]:focus-within {
    border-color: #548bd5 !important;
    box-shadow: 0 0 24px rgba(49, 147, 255, .12);
}

[data-testid="stChatInput"] textarea {
    color: #f0f4ff !important;
}

.stButton > button {
    min-height: 44px;
    border-radius: 13px;
    border: 1px solid #283553;
    background: linear-gradient(130deg, #10182b, #121024);
    color: #eaf1ff;
    transition: all .2s ease;
}

.stButton > button:hover {
    border-color: #66c9ff;
    background: linear-gradient(130deg, #152745, #21183b);
    box-shadow: 0 0 20px rgba(76, 166, 255, .13);
    color: white;
}

div[data-testid="stMetric"] {
    background: #0d1120;
    border: 1px solid #222b45;
    padding: 12px;
    border-radius: 12px;
}

hr {
    border-color: #20263b;
}

footer {
    visibility: hidden;
}

#MainMenu {
    visibility: hidden;
}

[data-testid="stDecoration"] {
    display: none;
}

.small-label {
    font-size: 10px;
    letter-spacing: 2.5px;
    color: #7887a8;
    text-transform: uppercase;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# ---------------- SIDEBAR ----------------

with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)
    else:
        st.markdown('<div class="brand-mark">Q U N I T</div>',
                    unsafe_allow_html=True)

    st.markdown("## SINGULARITY")
    st.caption("BEYOND THE KNOWN")
    st.divider()

    if st.button("＋   New conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.rerun()

    st.markdown('<div class="small-label">SYSTEM</div>',
                unsafe_allow_html=True)
    st.write("Cloud engine")
    st.caption(MODEL)

    if API_KEY:
        st.success("API key configured")
    else:
        st.warning("API key not configured")

    st.divider()

    st.markdown('<div class="small-label">CREATED BY</div>',
                unsafe_allow_html=True)
    st.markdown("**QUNIT**")
    st.caption("Discover. Create. Explore.")

    st.markdown("---")
    st.caption("SINGULARITY AI · QUNIT")

# ---------------- OPENROUTER ----------------

def ask_openrouter(messages):
    if not API_KEY:
        return (
            "Your cloud API key is missing. Add "
            "`OPENROUTER_API_KEY` in Streamlit Secrets."
        )

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages,
        ],
        "temperature": 0.7,
        "max_tokens": 800,
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
            return "The provider reports insufficient credits or balance."
        if response.status_code == 403:
            return "The provider denied access to this request or model."
        if response.status_code == 404:
            return "The model was not found. Check OPENROUTER_MODEL."
        if response.status_code == 429:
            return "The service is busy or rate-limited. Try again shortly."

        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    except requests.Timeout:
        return "The response took too long. Please try again."
    except requests.RequestException:
        return "Could not reach the cloud AI service. Check your connection."
    except (KeyError, IndexError, ValueError):
        return "The AI service returned an unexpected response."

# ---------------- MAIN HEADER ----------------

if not st.session_state.messages:
    st.markdown('<div class="hero">', unsafe_allow_html=True)

    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=235)

    st.markdown(
        '<div class="eyebrow">QUNIT PRESENTS</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="brand-title">Think beyond the known.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="intro">'
        'A space for questions, ideas, discoveries, and things '
        'you have not imagined yet.'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="small-label">CHOOSE YOUR STARTING POINT</div>',
                unsafe_allow_html=True)
    st.write("")

    suggestions = [
        ("01", "Explore the universe",
         "Explain black holes and the mysteries of space."),
        ("02", "Invent something",
         "Give me an original invention idea."),
        ("03", "Solve a challenge",
         "Help me solve a difficult problem step by step."),
    ]

    columns = st.columns(3)

    for i, (number, title, prompt_text) in enumerate(suggestions):
        with columns[i]:
            st.markdown(f"**{number} / {title}**")
            st.caption(prompt_text)
            if st.button("Explore ↗", key=f"suggestion_{i}",
                         use_container_width=True):
                st.session_state.pending_prompt = prompt_text
                st.rerun()
else:
    st.markdown(
        '<div class="brand-mark">S I N G U L A R I T Y  /  C H A T</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### Your conversation")

# ---------------- CHAT HISTORY ----------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- USER INPUT ----------------

prompt = st.chat_input("Ask a question. Explore an idea.")

if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Exploring the possibilities..."):
            answer = ask_openrouter(st.session_state.messages)
        st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
    })

st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#64708e;font-size:10px;'
    'letter-spacing:2px;">SINGULARITY AI · POWERED BY QUNIT</div>',
    unsafe_allow_html=True,
)

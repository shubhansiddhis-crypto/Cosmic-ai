
import os
import base64
from pathlib import Path

import requests
import streamlit as st

# =========================================================
# SINGULARITY AI | BY QUNIT
# Complete Streamlit application
# =========================================================

st.set_page_config(
    page_title="SINGULARITY AI | QUNIT",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------- CONFIG -------------------------

APP_DIR = Path(__file__).parent
LOGO_PATH = APP_DIR / "singularity_logo.png"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

DEFAULT_MODEL = "openrouter/free"

SYSTEM_PROMPT = """
You are SINGULARITY AI, created by QUNIT.

Be intelligent, helpful, accurate, creative, and clear.
Explain difficult concepts in simple language when appropriate.
Use readable formatting, examples, and step-by-step reasoning.
Be honest when uncertain. Never invent facts or sources.
Adapt your response to the user's question and requested detail.
"""

# ------------------------- SECRETS -------------------------

def get_secret(name, fallback=""):
    try:
        return str(st.secrets.get(name, fallback)).strip()
    except Exception:
        return str(fallback).strip()


API_KEY = get_secret("OPENROUTER_API_KEY")
MODEL = get_secret("OPENROUTER_MODEL", DEFAULT_MODEL)

if not MODEL:
    MODEL = DEFAULT_MODEL

# ------------------------- SESSION STATE -------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "input_counter" not in st.session_state:
    st.session_state.input_counter = 0

if "last_error" not in st.session_state:
    st.session_state.last_error = ""

# ------------------------- OPTIONAL LOGO -------------------------

def get_logo_data():
    if not LOGO_PATH.exists():
        return None

    try:
        encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
    except Exception:
        return None


LOGO_DATA = get_logo_data()

# ------------------------- DESIGN SYSTEM -------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    :root {
        --bg: #05050b;
        --panel: rgba(15, 16, 32, 0.76);
        --border: rgba(139, 135, 255, 0.19);
        --blue: #6c8dff;
        --violet: #a875ff;
        --text: #f5f5ff;
        --muted: #9798b8;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse at 50% -12%, rgba(93, 77, 255, 0.18), transparent 43%),
            radial-gradient(ellipse at 95% 45%, rgba(44, 90, 255, 0.07), transparent 35%),
            #05050b !important;
        color: var(--text);
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    [data-testid="stToolbar"],
    #MainMenu,
    footer {
        visibility: hidden;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1440px;
        padding: 1.1rem clamp(1rem, 4vw, 3.5rem) 2rem;
    }

    /* Top navigation */

    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        padding: 10px 0 22px;
        border-bottom: 1px solid rgba(160, 155, 255, 0.13);
        margin-bottom: 25px;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 13px;
        min-width: 0;
    }

    .brand-icon {
        width: 46px;
        height: 46px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 15px;
        overflow: hidden;
        flex-shrink: 0;
        background: linear-gradient(145deg, #20224b, #10101c);
        border: 1px solid rgba(154, 135, 255, .5);
        box-shadow: 0 0 26px rgba(108, 91, 255, .18);
    }

    .brand-icon img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .brand-icon .fallback {
        font-size: 27px;
        line-height: 1;
    }

    .brand-name {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 17px;
        font-weight: 700;
        letter-spacing: 1.4px;
        color: #fff;
    }

    .brand-byline {
        color: #9c9abb;
        font-size: 10px;
        letter-spacing: 2px;
        margin-top: 4px;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 9px 13px;
        border: 1px solid rgba(130, 130, 180, .2);
        border-radius: 30px;
        color: #c6c6df;
        background: rgba(19, 20, 40, .7);
        font-size: 11px;
        white-space: nowrap;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        background: #a78bfa;
        border-radius: 50%;
        box-shadow: 0 0 10px #a78bfa;
    }

    /* Hero */

    .hero {
        text-align: center;
        padding: 17px 0 14px;
    }

    .hero-emblem {
        width: 180px;
        height: 180px;
        margin: 0 auto 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        border-radius: 50%;
        background:
            radial-gradient(circle at 50% 48%,
                rgba(5, 5, 14, 1) 0%,
                rgba(8, 8, 20, 1) 26%,
                rgba(81, 66, 190, .28) 39%,
                rgba(45, 99, 255, .14) 52%,
                transparent 70%);
        border: 1px solid rgba(137, 119, 255, .2);
        box-shadow:
            0 0 38px rgba(96, 77, 255, .13),
            inset 0 0 36px rgba(86, 75, 255, .08);
    }

    .hero-emblem:before {
        content: "";
        position: absolute;
        inset: 13px;
        border-radius: 50%;
        border: 1px solid rgba(111, 156, 255, .45);
        box-shadow: 0 0 20px rgba(108, 141, 255, .12);
    }

    .hero-emblem:after {
        content: "";
        position: absolute;
        width: 205px;
        height: 63px;
        border: 2px solid transparent;
        border-top-color: rgba(163, 128, 255, .85);
        border-bottom-color: rgba(79, 159, 255, .65);
        border-radius: 50%;
        transform: rotate(-28deg);
        filter: drop-shadow(0 0 7px rgba(127, 112, 255, .6));
    }

    .hero-emblem img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 50%;
        position: relative;
        z-index: 2;
    }

    .singularity-core {
        position: relative;
        z-index: 1;
        width: 61px;
        height: 61px;
        border-radius: 50%;
        background: radial-gradient(circle at 40% 35%, #20203c 0%, #030309 56%, #000 72%);
        box-shadow:
            0 0 0 5px rgba(143, 113, 255, .08),
            0 0 20px rgba(105, 120, 255, .8),
            0 0 43px rgba(126, 74, 255, .5);
    }

    .hero-kicker {
        color: #a99cff;
        font-size: 10px;
        letter-spacing: 4px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(27px, 4.5vw, 46px);
        font-weight: 700;
        line-height: 1.12;
        letter-spacing: clamp(1px, .4vw, 4px);
        margin: 0;
        color: #fff;
        text-shadow: 0 0 35px rgba(137, 120, 255, .17);
    }

    .hero-title span {
        background: linear-gradient(100deg, #e3e3ff 5%, #9b9cff 45%, #c49bff 80%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        color: #9b9ab8;
        font-size: 13px;
        line-height: 1.7;
        margin: 13px auto 0;
        max-width: 480px;
    }

    /* Section labels */

    .section-label {
        color: #aaa8ce;
        font-size: 10px;
        letter-spacing: 2.4px;
        font-weight: 700;
        margin: 24px 0 12px;
    }

    /* Suggestion cards */

    div[data-testid="stHorizontalBlock"] {
        gap: 12px;
    }

    .suggestion-note {
        font-size: 11px;
        color: #8585a6;
        margin: 4px 0 10px;
    }

    .stButton > button {
        border: 1px solid rgba(137, 132, 211, .23);
        border-radius: 13px;
        background: linear-gradient(145deg, rgba(21, 22, 45, .96), rgba(12, 13, 27, .96));
        color: #e8e7ff;
        min-height: 48px;
        padding: 11px 14px;
        font-size: 12px;
        font-weight: 500;
        transition: border-color .2s, background .2s, transform .2s;
        width: 100%;
    }

    .stButton > button:hover {
        border-color: rgba(152, 128, 255, .8);
        background: linear-gradient(145deg, rgba(40, 35, 81, .96), rgba(17, 20, 45, .96));
        color: white;
        transform: translateY(-1px);
    }

    .stButton > button:focus {
        box-shadow: 0 0 0 2px rgba(139, 119, 255, .2);
        border-color: #a18aff;
    }

    /* Chat */

    [data-testid="stChatMessage"] {
        background: rgba(14, 15, 31, .73);
        border: 1px solid rgba(135, 131, 200, .16);
        border-radius: 17px;
        padding: 17px 18px;
        margin-bottom: 13px;
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        color: #ecebff;
        line-height: 1.75;
        font-size: 14px;
    }

    [data-testid="stChatMessageAvatarIcon"] {
        background: rgba(104, 94, 206, .18);
        border-radius: 50%;
    }

    /* Composer */

    [data-testid="stChatInput"] {
        border-radius: 18px;
    }

    [data-testid="stChatInput"] > div {
        border: 1px solid rgba(145, 130, 255, .35) !important;
        border-radius: 18px !important;
        background: rgba(13, 14, 30, .97) !important;
        box-shadow: 0 0 35px rgba(73, 68, 180, .09);
    }

    [data-testid="stChatInput"] textarea {
        color: #f5f4ff !important;
        font-size: 14px !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #7f809f !important;
    }

    [data-testid="stChatInput"] button {
        color: #c7b9ff !important;
    }

    /* Inputs and utility controls */

    .stTextInput input,
    .stSelectbox div[data-baseweb="select"] > div {
        background: #101124;
        color: #f2f0ff;
        border-color: rgba(137, 132, 211, .25);
        border-radius: 10px;
    }

    .stAlert {
        border-radius: 12px;
    }

    .bottom-caption {
        text-align: center;
        color: #666782;
        font-size: 10px;
        letter-spacing: 1.2px;
        margin-top: 19px;
        padding: 15px 0;
    }

    .empty-space {
        height: 6px;
    }

    @media (max-width: 640px) {
        [data-testid="stMainBlockContainer"] {
            padding: .7rem .85rem 1.5rem;
        }

        .hero {
            padding-top: 12px;
        }

        .hero-emblem {
            width: 145px;
            height: 145px;
        }

        .hero-emblem:after {
            width: 165px;
            height: 49px;
        }

        .brand-name {
            font-size: 13px;
            letter-spacing: .7px;
        }

        .brand-byline {
            font-size: 8px;
            letter-spacing: 1px;
        }

        .status-pill {
            padding: 8px;
            font-size: 9px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------- HEADER -------------------------

logo_html = (
    f'<img src="{LOGO_DATA}" alt="Singularity emblem">'
    if LOGO_DATA
    else '<span class="fallback">✦</span>'
)

st.markdown(
    f"""
    <div class="topbar">
        <div class="brand">
            <div class="brand-icon">{logo_html}</div>
            <div>
                <div class="brand-name">SINGULARITY AI</div>
                <div class="brand-byline">A QUNIT INTELLIGENCE PROJECT</div>
            </div>
        </div>
        <div class="status-pill">
            <span class="status-dot"></span>
            CLOUD AI
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------- CHAT ACTIONS -------------------------

def reset_chat():
    st.session_state.messages = []
    st.session_state.last_error = ""


# ------------------------- HERO / EMPTY STATE -------------------------

if not st.session_state.messages:
    if LOGO_DATA:
        hero_art = f'<img src="{LOGO_DATA}" alt="Singularity AI emblem">'
    else:
        hero_art = '<div class="singularity-core"></div>'

    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-emblem">{hero_art}</div>
            <div class="hero-kicker">BEYOND THE KNOWN</div>
            <h1 class="hero-title">ENTER THE <span>SINGULARITY</span></h1>
            <div class="hero-subtitle">
                An intelligence for ideas, discovery, and the questions
                that take you beyond the ordinary.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-label">✦ &nbsp; CHOOSE YOUR NEXT EXPLORATION</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="suggestion-note">Start with a prompt or type your own below.</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("◈  Explain a mind-bending science idea", use_container_width=True):
            st.session_state.pending_prompt = (
                "Explain a mind-bending science idea in an engaging, accurate way."
            )
            st.rerun()

        if st.button("⌘  Build something with code", use_container_width=True):
            st.session_state.pending_prompt = (
                "Help me build a useful project with code, step by step."
            )
            st.rerun()

    with col2:
        if st.button("✧  Invent something extraordinary", use_container_width=True):
            st.session_state.pending_prompt = (
                "Help me invent an original, realistic project idea with a clear plan."
            )
            st.rerun()

        if st.button("⟡  Explore the universe", use_container_width=True):
            st.session_state.pending_prompt = (
                "Tell me about a fascinating unsolved question in astronomy."
            )
            st.rerun()

else:
    st.markdown(
        '<div class="section-label">✦ &nbsp; YOUR CONVERSATION</div>',
        unsafe_allow_html=True,
    )

    top_left, top_right = st.columns([5, 1])

    with top_right:
        if st.button("＋ New chat", use_container_width=True):
            reset_chat()
            st.rerun()

    for message in st.session_state.messages:
        avatar = "✦" if message["role"] == "assistant" else "●"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# ------------------------- CONNECTION CHECK -------------------------

if not API_KEY:
    st.warning(
        "Cloud AI is not configured yet. Add OPENROUTER_API_KEY "
        "in your Streamlit app's Secrets settings to start chatting."
    )

# ------------------------- SEND MESSAGE -------------------------

prompt = st.chat_input("Ask anything. Explore beyond the known...")

pending_prompt = st.session_state.pop("pending_prompt", None)

if pending_prompt:
    prompt = pending_prompt

if prompt:
    prompt = prompt.strip()

    if prompt:
        st.session_state.messages.append(
            {"role": "user", "content": prompt}
        )
        st.session_state.last_error = ""

        with st.chat_message("user", avatar="●"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="✦"):
            response_placeholder = st.empty()

            if not API_KEY:
                answer = (
                    "Cloud AI is not configured yet. Open your Streamlit "
                    "app's Settings or Manage app menu, find Secrets, and "
                    "add your OpenRouter API key as OPENROUTER_API_KEY. "
                    "Keep the key private."
                )
                response_placeholder.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
            else:
                try:
                    api_messages = [
                        {"role": "system", "content": SYSTEM_PROMPT}
                    ]

                    # Send recent conversation context to the model.
                    for item in st.session_state.messages[-20:]:
                        api_messages.append(
                            {
                                "role": item["role"],
                                "content": item["content"],
                            }
                        )

                    payload = {
                        "model": MODEL,
                        "messages": api_messages,
                        "temperature": 0.7,
                        "max_tokens": 1200,
                        "stream": False,
                    }

                    headers = {
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": (
                            "https://cosmic-ai-bkndcuztfxpmrdzrnsrtmj.streamlit.app/"
                        ),
                        "X-Title": "SINGULARITY AI by QUNIT",
                    }

                    response = requests.post(
                        OPENROUTER_URL,
                        headers=headers,
                        json=payload,
                        timeout=90,
                    )

                    if not response.ok:
                        try:
                            error_data = response.json()
                            error_message = (
                                error_data.get("error", {}).get(
                                    "message", response.text
                                )
                            )
                        except Exception:
                            error_message = response.text

                        raise RuntimeError(
                            f"OpenRouter returned HTTP {response.status_code}: "
                            f"{error_message}"
                        )

                    data = response.json()
                    choices = data.get("choices", [])

                    if not choices:
                        raise RuntimeError(
                            "The AI provider returned no answer. "
                            "Try again in a moment."
                        )

                    answer = (
                        choices[0]
                        .get("message", {})
                        .get("content", "")
                    )

                    if isinstance(answer, list):
                        answer = "\n".join(
                            part.get("text", "")
                            for part in answer
                            if isinstance(part, dict)
                        )

                    answer = str(answer).strip()

                    if not answer:
                        answer = "I couldn't produce a response this time. Please try again."

                    response_placeholder.markdown(answer)

                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )

                except requests.Timeout:
                    answer = (
                        "The request took too long. The free model may be "
                        "busy. Please try again shortly."
                    )
                    response_placeholder.error(answer)
                    st.session_state.last_error = answer

                except requests.RequestException:
                    answer = (
                        "I couldn't connect to the AI service. Check your "
                        "internet connection and try again."
                    )
                    response_placeholder.error(answer)
                    st.session_state.last_error = answer

                except Exception as error:
                    # Display a useful diagnostic without exposing the API key.
                    answer = (
                        "The AI request failed. Check your OpenRouter model "
                        "and account availability in Streamlit Secrets. "
                        f"Details: {str(error)[:500]}"
                    )
                    response_placeholder.error(answer)
                    st.session_state.last_error = answer

                if st.session_state.last_error:
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": st.session_state.last_error,
                        }
                    )

        st.rerun()

# ------------------------- FOOTER -------------------------

st.markdown(
    """
    <div class="bottom-caption">
        SINGULARITY AI &nbsp; · &nbsp; CREATED BY QUNIT
        <br><br>
        THINK DEEPER. BUILD FURTHER. EXPLORE THE UNKNOWN.
    </div>
    """,
    unsafe_allow_html=True,
)

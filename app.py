
import base64
from pathlib import Path

import requests
import streamlit as st

# =========================================================
# SINGULARITY AI | BY QUNIT
# =========================================================

st.set_page_config(
    page_title="SINGULARITY AI | QUNIT",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = Path(__file__).parent
LOGO_PATH = APP_DIR / "singularity_logo.png"

API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openrouter/free"

SYSTEM_PROMPT = """
You are SINGULARITY AI, created by QUNIT.

Be intelligent, helpful, creative, clear, and accurate.
Explain difficult concepts simply when useful.
Use examples and step-by-step explanations when appropriate.
Be honest when uncertain. Never invent facts or sources.
Adapt your response to the user's question.
"""

# =========================================================
# SECRETS
# =========================================================

def get_secret(name, default=""):
    try:
        return str(st.secrets.get(name, default)).strip()
    except Exception:
        return default


API_KEY = get_secret("OPENROUTER_API_KEY")
MODEL = get_secret("OPENROUTER_MODEL", DEFAULT_MODEL) or DEFAULT_MODEL

# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# =========================================================
# LOGO
# =========================================================

def load_logo():
    try:
        if LOGO_PATH.is_file():
            return base64.b64encode(LOGO_PATH.read_bytes()).decode("utf-8")
    except OSError:
        pass
    return None


LOGO = load_logo()

# =========================================================
# STYLING
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg: #06060c;
    --blue: #7194ff;
    --purple: #a17bff;
    --muted: #9999b7;
}

html, body, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse at 50% -10%, rgba(91,72,220,.23), transparent 45%),
        radial-gradient(ellipse at 95% 40%, rgba(48,84,255,.07), transparent 35%),
        #06060c !important;
    color: #f5f4ff;
    font-family: 'Inter', sans-serif;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stMainBlockContainer"] {
    max-width: 1450px;
    padding-top: 1.1rem;
    padding-bottom: 2rem;
}

#MainMenu, footer {
    visibility: hidden;
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101020, #090910);
    border-right: 1px solid rgba(151,130,255,.2);
}

[data-testid="stSidebar"] * {
    color: #e8e6ff;
}

.sidebar-brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 1px;
}

.sidebar-caption {
    font-size: 10px;
    letter-spacing: 2px;
    color: #a89bff !important;
    margin-top: 5px;
}

.sidebar-status {
    border: 1px solid rgba(151,130,255,.23);
    border-radius: 12px;
    background: rgba(24,24,47,.8);
    padding: 12px;
    font-size: 12px;
    line-height: 1.9;
    margin: 12px 0;
}

/* TOP NAVIGATION */

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 5px 0 20px;
    border-bottom: 1px solid rgba(151,130,255,.17);
    margin-bottom: 22px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 0;
}

.brand-icon {
    width: 48px;
    height: 48px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    border-radius: 12px;
    background: linear-gradient(145deg,#24244b,#101020);
    border: 1px solid rgba(155,130,255,.45);
    box-shadow: 0 0 25px rgba(109,92,255,.17);
    font-size: 26px;
}

.brand-icon img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: contain;
    border-radius: 0;
}

.brand-name {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 16px;
    letter-spacing: 1.2px;
}

.brand-sub {
    color: #9998b8;
    font-size: 10px;
    letter-spacing: 1.5px;
    margin-top: 4px;
}

.pill {
    border: 1px solid rgba(139,132,213,.24);
    border-radius: 30px;
    padding: 8px 12px;
    background: rgba(20,20,40,.7);
    font-size: 11px;
    color: #c8c5ec;
    white-space: nowrap;
}

/* CENTRAL EMBLEM */

.hero {
    text-align: center;
    padding: 15px 0 18px;
}

/* Fallback emblem, used only if the PNG is missing */

.emblem {
    width: 250px;
    height: 250px;
    max-width: 90%;
    margin: 0 auto 23px;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background:
        radial-gradient(circle at center,
            #000 0%,
            #02020b 18%,
            rgba(67,52,160,.48) 32%,
            rgba(74,111,255,.22) 48%,
            transparent 70%);
    border: 1px solid rgba(126,111,255,.35);
    box-shadow:
        0 0 35px rgba(94,78,255,.25),
        0 0 80px rgba(99,75,255,.16),
        inset 0 0 35px rgba(92,108,255,.13);
}

.emblem:before {
    content: "";
    position: absolute;
    inset: 23px;
    border-radius: 50%;
    border: 3px solid transparent;
    border-top-color: #a78bfa;
    border-bottom-color: #5b9bff;
    transform: rotate(-24deg);
    box-shadow: 0 0 19px rgba(118,112,255,.55);
}

.emblem:after {
    content: "";
    position: absolute;
    width: 285px;
    height: 86px;
    max-width: 112%;
    border-radius: 50%;
    border: 3px solid transparent;
    border-top-color: #d2a6ff;
    border-bottom-color: #4d9dff;
    transform: rotate(-28deg);
    filter: drop-shadow(0 0 7px #7667ff);
}

.core {
    width: 94px;
    height: 94px;
    border-radius: 50%;
    position: relative;
    z-index: 1;
    background: radial-gradient(circle at 35% 30%, #17152c 0%, #05050c 43%, #000 72%);
    box-shadow:
        0 0 0 8px rgba(132,111,255,.08),
        0 0 25px rgba(111,101,255,.95),
        0 0 55px rgba(123,73,255,.75),
        0 0 90px rgba(65,112,255,.35);
}

/*
If a logo image is present, disable the circular frame and
decorative rings so the complete original image stays visible.
*/

.emblem:has(img) {
    width: min(430px, 90%);
    height: auto;
    aspect-ratio: auto;
    display: block;
    background: transparent;
    border: none;
    border-radius: 0;
    box-shadow: none;
    overflow: visible;
}

.emblem:has(img):before,
.emblem:has(img):after {
    display: none;
}

.emblem img {
    position: relative;
    z-index: 2;
    display: block;
    width: 100%;
    height: auto;
    max-height: 360px;
    object-fit: contain;
    object-position: center;
    border-radius: 0;
    margin: 0 auto;
    filter: drop-shadow(0 0 22px rgba(110,91,255,.22));
}

.kicker {
    color: #b3a0ff;
    font-size: 10px;
    letter-spacing: 4px;
    font-weight: 700;
    margin-bottom: 10px;
}

.hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(26px,4.2vw,45px);
    letter-spacing: 2px;
    line-height: 1.2;
    margin: 0;
    color: #fff;
}

.hero h1 span {
    background: linear-gradient(100deg,#a4b9ff,#c19bff);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-description {
    color: var(--muted);
    max-width: 490px;
    margin: 13px auto 20px;
    line-height: 1.8;
    font-size: 13px;
}

.section-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #aaa6d4;
    margin: 20px 0 12px;
}

/* BUTTONS */

.stButton > button {
    border: 1px solid rgba(139,132,213,.25);
    border-radius: 12px;
    background: linear-gradient(140deg,rgba(25,25,52,.98),rgba(13,14,29,.98));
    color: #eceaff;
    min-height: 46px;
    font-size: 12px;
    transition: .2s ease;
}

.stButton > button:hover {
    border-color: #9d8aff;
    background: linear-gradient(140deg,#28234c,#171831);
    color: #fff;
}

/* CHAT */

[data-testid="stChatMessage"] {
    background: rgba(17,17,35,.8);
    border: 1px solid rgba(139,132,213,.18);
    border-radius: 15px;
    padding: 14px 16px;
    margin-bottom: 12px;
}

[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
    color: #eeedff;
    font-size: 14px;
    line-height: 1.8;
}

[data-testid="stChatInput"] > div {
    background: #111124 !important;
    border: 1px solid rgba(146,128,255,.4) !important;
    border-radius: 16px !important;
    box-shadow: 0 0 24px rgba(95,79,210,.09);
}

[data-testid="stChatInput"] textarea {
    color: #fff !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #7f809f !important;
}

.footer {
    color: #777794;
    text-align: center;
    font-size: 10px;
    letter-spacing: 1.5px;
    padding: 20px 0 10px;
}

@media (max-width: 640px) {
    [data-testid="stMainBlockContainer"] {
        padding-left: .8rem;
        padding-right: .8rem;
    }

    .emblem {
        width: 190px;
        height: 190px;
    }

    .emblem:after {
        width: 215px;
        height: 65px;
    }

    .emblem:has(img) {
        width: min(320px, 92%);
        height: auto;
    }

    .brand-name {
        font-size: 12px;
    }

    .brand-sub {
        font-size: 8px;
        letter-spacing: .8px;
    }
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand">✦ SINGULARITY</div>'
        '<div class="sidebar-caption">QUNIT INTELLIGENCE SYSTEM</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    if st.button("＋  New conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.rerun()

    st.markdown("### Control centre")

    connection_status = "Configured" if API_KEY else "API key required"

    st.markdown(
        f"""
        <div class="sidebar-status">
            <b>AI ENGINE</b><br>
            OpenRouter Cloud<br><br>
            <b>CONNECTION</b><br>
            {connection_status}<br><br>
            <b>MODEL</b><br>
            {MODEL}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption("Chat history lasts for the current app session.")

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.rerun()

    st.divider()
    st.caption("SINGULARITY AI · BY QUNIT")
    st.caption("Think deeper. Explore further.")

# =========================================================
# HEADER
# =========================================================

if LOGO:
    brand_icon = f'<img src="data:image/png;base64,{LOGO}" alt="Singularity logo">'
else:
    brand_icon = "✦"

st.markdown(
    f"""
    <div class="topbar">
        <div class="brand">
            <div class="brand-icon">{brand_icon}</div>
            <div>
                <div class="brand-name">SINGULARITY AI</div>
                <div class="brand-sub">CREATED BY QUNIT · BEYOND THE KNOWN</div>
            </div>
        </div>
        <div class="pill">✦ CLOUD AI</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# HOME SCREEN
# =========================================================

if not st.session_state.messages:
    if LOGO:
        emblem_content = (
            f'<img src="data:image/png;base64,{LOGO}" '
            'alt="Singularity black hole emblem">'
        )
    else:
        emblem_content = '<div class="core"></div>'

    st.markdown(
        f"""
        <div class="hero">
            <div class="emblem">{emblem_content}</div>
            <div class="kicker">BEYOND THE KNOWN</div>
            <h1>ENTER THE <span>SINGULARITY</span></h1>
            <div class="hero-description">
                An intelligence for ideas, discovery, and the questions
                that take you beyond the ordinary.
            </div>
        </div>
        <div class="section-label">✦ &nbsp; CHOOSE YOUR EXPLORATION</div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)

    with left:
        if st.button(
            "◈  Explore a mind-bending science idea",
            use_container_width=True,
        ):
            st.session_state.pending_prompt = (
                "Explain a mind-bending science idea in an engaging, accurate way."
            )
            st.rerun()

        if st.button("⌘  Build something with code", use_container_width=True):
            st.session_state.pending_prompt = (
                "Help me build a useful coding project step by step."
            )
            st.rerun()

    with right:
        if st.button(
            "✧  Invent something extraordinary",
            use_container_width=True,
        ):
            st.session_state.pending_prompt = (
                "Help me develop an original, realistic invention idea."
            )
            st.rerun()

        if st.button("⟡  Explore the universe", use_container_width=True):
            st.session_state.pending_prompt = (
                "Explain a fascinating question about the universe."
            )
            st.rerun()

else:
    st.markdown(
        '<div class="section-label">✦ &nbsp; YOUR CONVERSATION</div>',
        unsafe_allow_html=True,
    )

    for message in st.session_state.messages:
        # Default avatars avoid Unicode avatar media-file errors.
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# =========================================================
# API CONFIGURATION NOTICE
# =========================================================

if not API_KEY:
    st.warning(
        "OpenRouter is not configured. Add OPENROUTER_API_KEY "
        "in your Streamlit app's Secrets settings."
    )

# =========================================================
# CHAT ENGINE
# =========================================================

prompt = st.chat_input("Ask anything. Explore beyond the known...")

if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if prompt:
    prompt = prompt.strip()

    if prompt:
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        answer = ""

        with st.chat_message("assistant"):
            if not API_KEY:
                answer = (
                    "I need an OpenRouter API key before I can answer. "
                    "Add OPENROUTER_API_KEY to Streamlit Secrets and try again."
                )
                st.warning(answer)

            else:
                try:
                    api_messages = [
                        {"role": "system", "content": SYSTEM_PROMPT}
                    ]
                    api_messages.extend(st.session_state.messages[-20:])

                    headers = {
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": (
                            "https://cosmic-ai-bkndcuztfxpmrdzrnsrtmj.streamlit.app/"
                        ),
                        "X-Title": "SINGULARITY AI by QUNIT",
                    }

                    payload = {
                        "model": MODEL,
                        "messages": api_messages,
                        "temperature": 0.7,
                        "max_tokens": 1200,
                        "stream": False,
                    }

                    with st.spinner("Connecting to the singularity..."):
                        response = requests.post(
                            API_URL,
                            headers=headers,
                            json=payload,
                            timeout=90,
                        )

                    if not response.ok:
                        try:
                            error_data = response.json()
                            details = error_data.get("error", {}).get(
                                "message", "The provider request failed."
                            )
                        except ValueError:
                            details = "The provider request failed."

                        raise RuntimeError(
                            f"HTTP {response.status_code}: {details}"
                        )

                    data = response.json()
                    choices = data.get("choices", [])

                    if not choices:
                        raise RuntimeError("The model returned no answer.")

                    answer = choices[0].get("message", {}).get("content", "")

                    if isinstance(answer, list):
                        answer = "\n".join(
                            part.get("text", "")
                            for part in answer
                            if isinstance(part, dict)
                        )

                    answer = str(answer).strip()

                    if not answer:
                        answer = "I couldn't generate a response. Please try again."

                    st.markdown(answer)

                except requests.Timeout:
                    answer = (
                        "The request timed out. The free model may be busy. "
                        "Please try again."
                    )
                    st.error(answer)

                except requests.RequestException:
                    answer = (
                        "Could not connect to OpenRouter. Check your internet "
                        "connection and try again."
                    )
                    st.error(answer)

                except Exception as exc:
                    answer = f"AI request failed: {str(exc)[:400]}"
                    st.error(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
        })

        st.rerun()

# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        SINGULARITY AI · CREATED BY QUNIT<br><br>
        THINK DEEPER. BUILD FURTHER. EXPLORE THE UNKNOWN.
    </div>
    """,
    unsafe_allow_html=True,
)

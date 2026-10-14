
import streamlit as st
import requests

# =========================================================
# COSMIC AI | QUNIT
# Cloud AI engine: OpenRouter
# =========================================================

st.set_page_config(
    page_title="COSMIC AI | QUNIT",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openrouter/free"

SYSTEM_PROMPT = """
You are COSMIC AI, created by QUNIT.

Be friendly, clear, creative, helpful, and accurate.
Explain difficult ideas in simple language.
Use examples when helpful.
Admit uncertainty instead of inventing facts.
Format answers using Markdown when useful.
Keep answers concise unless more detail is requested.
"""

# -------------------- COSMIC DESIGN --------------------

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(ellipse at top, #1b2b50 0%, transparent 48%),
        linear-gradient(150deg, #080d1c, #0b1022 60%, #10182c);
    color: #edf2ff;
}
.block-container {
    max-width: 1050px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}
h1 {
    color: #c2d6ff;
    text-align: center;
    letter-spacing: 2px;
}
.subtitle {
    text-align: center;
    color: #a9bce4;
    margin-bottom: 2rem;
}
[data-testid="stChatMessage"] {
    background: rgba(31, 46, 78, 0.65);
    border: 1px solid #35476d;
    border-radius: 18px;
    padding: 14px;
    margin-bottom: 12px;
}
section[data-testid="stSidebar"] {
    background: #0c1326;
    border-right: 1px solid #273858;
}
.stButton button {
    border-radius: 12px;
    border: 1px solid #4e669b;
}
[data-testid="stChatInput"] {
    border-color: #536da5;
}
</style>
""", unsafe_allow_html=True)

# -------------------- SETTINGS --------------------

def get_setting(name, default=""):
    """Read settings from Streamlit Secrets, then environment."""
    try:
        value = st.secrets.get(name, default)
        if value:
            return str(value).strip()
    except Exception:
        pass

    import os
    return os.environ.get(name, default).strip()


def get_api_key():
    return get_setting("OPENROUTER_API_KEY")


def get_model():
    return get_setting("OPENROUTER_MODEL", DEFAULT_MODEL)


# -------------------- AI ENGINE --------------------

def ask_openrouter(messages):
    api_key = get_api_key()
    model = get_model()

    if not api_key:
        return None, (
            "The OpenRouter API key is missing. Open your Streamlit "
            "app's Settings → Secrets and add OPENROUTER_API_KEY."
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": (
            "https://cosmic-ai-bkndcuztfxpmrdzrnsrtmj.streamlit.app/"
        ),
        "X-Title": "COSMIC AI | QUNIT",
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages,
        ],
        "temperature": 0.7,
        "max_tokens": 700,
    }

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=90,
        )

        if response.status_code == 401:
            return None, (
                "OpenRouter rejected the API key (401). Check that "
                "your key is valid, active, and saved correctly."
            )

        if response.status_code == 402:
            return None, (
                "OpenRouter reports insufficient credits or unavailable "
                "account balance for this request. Check your account "
                "and the selected model's requirements."
            )

        if response.status_code == 403:
            return None, (
                "OpenRouter denied this request (403). Check model "
                "access, account restrictions, or provider requirements."
            )

        if response.status_code == 404:
            return None, (
                f"The requested model was not found: {model}. "
                "Check the model name or try another available model."
            )

        if response.status_code == 429:
            return None, (
                "OpenRouter rate limit reached. Wait a little and try "
                "again, or check the free model's usage limits."
            )

        response.raise_for_status()
        data = response.json()

        choices = data.get("choices", [])
        if not choices:
            return None, (
                "The API responded, but no answer was returned. "
                "Try again or check model availability."
            )

        answer = choices[0].get("message", {}).get("content", "")
        if not answer:
            return None, "The AI returned an empty answer. Please try again."

        return answer, None

    except requests.exceptions.Timeout:
        return None, (
            "The AI took too long to respond. Please try again."
        )

    except requests.exceptions.HTTPError as error:
        status = (
            error.response.status_code
            if error.response is not None
            else "unknown"
        )
        return None, (
            f"OpenRouter returned HTTP {status}. "
            "Check your OpenRouter account and model availability."
        )

    except requests.exceptions.RequestException:
        return None, (
            "COSMIC AI couldn't reach OpenRouter. Check your internet "
            "connection and try again."
        )

    except (ValueError, KeyError, TypeError):
        return None, (
            "COSMIC AI received an unexpected response. Please try again."
        )


# -------------------- SESSION --------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_error" not in st.session_state:
    st.session_state.last_error = None

# -------------------- SIDEBAR --------------------

with st.sidebar:
    st.markdown("## 🪐 COSMIC CONTROL")
    st.caption("QUNIT AI SYSTEM")
    st.markdown("---")

    if get_api_key():
        st.success("🔑 API key detected")
        st.caption("This checks whether a key is configured, "
                   "not whether the key is valid.")
    else:
        st.warning("🔑 API key not detected")

    st.caption(f"Engine: OpenRouter")
    st.caption(f"Model: {get_model()}")

    st.markdown("---")

    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_error = None
        st.rerun()

    st.markdown("---")
    st.caption("COSMIC AI · POWERED BY QUNIT")
    st.caption("Cloud access requires internet.")

# -------------------- MAIN INTERFACE --------------------

st.title("🌌 COSMIC AI")
st.markdown(
    '<p class="subtitle">'
    'CREATED BY QUNIT · YOUR UNIVERSE OF IDEAS'
    '</p>',
    unsafe_allow_html=True,
)

if not st.session_state.messages:
    st.markdown("### ✨ Welcome, explorer.")
    st.write(
        "Your universe of ideas starts here. Ask a question, "
        "explore a concept, or build something new."
    )

    st.markdown("**Try asking:**")
    col1, col2, col3 = st.columns(3)

    if col1.button("🪐 Explain black holes", use_container_width=True):
        st.session_state.pending_prompt = (
            "Explain black holes in simple language."
        )
        st.rerun()

    if col2.button("💡 Invent a project", use_container_width=True):
        st.session_state.pending_prompt = (
            "Suggest an original science project for QUNIT."
        )
        st.rerun()

    if col3.button("🚀 Explore space", use_container_width=True):
        st.session_state.pending_prompt = (
            "Tell me three fascinating facts about space."
        )
        st.rerun()

# Display existing messages
for message in st.session_state.messages:
    avatar = "🧑‍🚀" if message["role"] == "user" else "🌌"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Accept either a typed prompt or a suggestion
typed_prompt = st.chat_input("Ask COSMIC AI anything...")
suggested_prompt = st.session_state.pop("pending_prompt", None)
prompt = typed_prompt or suggested_prompt

if prompt:
    st.session_state.last_error = None

    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user", avatar="🧑‍🚀"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🌌"):
        with st.spinner("COSMIC AI is thinking..."):
            answer, error_message = ask_openrouter(
                st.session_state.messages
            )

        if answer:
            st.markdown(answer)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )
        else:
            st.session_state.last_error = error_message
            st.error(error_message)

    st.rerun()

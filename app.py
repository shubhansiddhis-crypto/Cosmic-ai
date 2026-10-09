
import streamlit as st

st.set_page_config(
    page_title="COSMIC AI | QUNIT",
    page_icon="🌌",
    layout="wide",
)

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
</style>
""", unsafe_allow_html=True)

SYSTEM_PROMPT = """
You are COSMIC AI, created by QUNIT.
Be friendly, clear, creative, and accurate.
Explain difficult ideas simply.
Admit uncertainty rather than inventing facts.
"""

st.title("🌌 COSMIC AI")
st.markdown(
    '<p class="subtitle">'
    'CREATED BY QUNIT · YOUR UNIVERSE OF IDEAS'
    '</p>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## 🪐 COSMIC CONTROL")
    st.caption("QUNIT AI SYSTEM")
    st.markdown("---")

    st.info("☁️ Cloud deployment preparation")
    st.caption("AI service: not connected yet")
    st.caption("Your API keys must stay in hosting secrets.")

    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("COSMIC AI · POWERED BY QUNIT")

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.markdown("### ✨ Welcome, explorer.")
    st.write(
        "COSMIC AI is preparing for launch. "
        "The cloud AI connection will be added once "
        "an approved service is available."
    )

for message in st.session_state.messages:
    avatar = "🧑‍🚀" if message["role"] == "user" else "🌌"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

prompt = st.chat_input("Try COSMIC AI...")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )
    with st.chat_message("user", avatar="🧑‍🚀"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🌌"):
        st.info(
            "🚀 COSMIC AI's cloud brain isn't connected yet. "
            "Your message hasn't been sent to an AI service. "
            "We'll enable real answers after configuring "
            "an approved cloud provider."
        )
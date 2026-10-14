
import base64
import uuid
from pathlib import Path
from urllib.parse import quote

import requests
import streamlit as st
from supabase import create_client

# =========================================================
# SINGULARITY AI | BY QUNIT
# =========================================================

st.set_page_config(
    page_title="SINGULARITY AI | QUNIT",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_URL = "https://singularity-ai-bkndcuztfxpmrdzrnsrtmj.streamlit.app"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openrouter/free"
LOGO_PATH = Path(__file__).parent / "singularity_logo.png"

SYSTEM_PROMPT = """
You are SINGULARITY AI, created by QUNIT.

Be intelligent, helpful, creative, clear, and accurate.
Explain difficult concepts simply when useful.
Use examples and step-by-step explanations when appropriate.
Be honest when uncertain. Never invent facts or sources.
Adapt your response to the user's question.
"""

def secret(name, default=""):
    try:
        return str(st.secrets.get(name, default)).strip()
    except Exception:
        return default

API_KEY = secret("OPENROUTER_API_KEY")
MODEL = secret("OPENROUTER_MODEL", DEFAULT_MODEL) or DEFAULT_MODEL
SUPABASE_URL = secret("SUPABASE_URL")
SUPABASE_KEY = secret("SUPABASE_KEY")

# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "sb_client": None,
    "user": None,
    "access_token": None,
    "refresh_token": None,
    "messages": [],
    "chat_id": None,
    "chat_list": [],
    "pending_prompt": None,
    "auth_notice": None,
    "last_auth_code": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# SUPABASE CONNECTION
# =========================================================

def get_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None

    if st.session_state.sb_client is None:
        st.session_state.sb_client = create_client(
            SUPABASE_URL, SUPABASE_KEY
        )

    return st.session_state.sb_client

def set_logged_in(session, user):
    st.session_state.access_token = session.access_token
    st.session_state.refresh_token = session.refresh_token
    st.session_state.user = {
        "id": str(user.id),
        "email": user.email or "",
    }

def restore_session(client):
    access = st.session_state.access_token
    refresh = st.session_state.refresh_token

    if not access or not refresh:
        return False

    try:
        result = client.auth.set_session(access, refresh)
        session = result.session
        user = result.user

        if session and user:
            set_logged_in(session, user)
            return True
    except Exception:
        st.session_state.access_token = None
        st.session_state.refresh_token = None
        st.session_state.user = None

    return False

sb = get_supabase()

# =========================================================
# AUTH CALLBACK
# =========================================================

if sb:
    code = st.query_params.get("code")

    if code and code != st.session_state.last_auth_code:
        try:
            result = sb.auth.exchange_code_for_session(
                {"auth_code": code}
            )

            if result.session and result.user:
                set_logged_in(result.session, result.user)
                st.session_state.last_auth_code = code
                st.query_params.clear()
                st.session_state.auth_notice = (
                    "You are signed in successfully."
                )
                st.rerun()

        except Exception:
            st.session_state.auth_notice = (
                "Google sign-in could not be completed. "
                "Please try signing in again."
            )
            st.query_params.clear()

    if not st.session_state.user:
        restore_session(sb)

# =========================================================
# STYLING
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse at 50% -10%,
            rgba(91,72,220,.23), transparent 45%),
        radial-gradient(ellipse at 95% 40%,
            rgba(48,84,255,.07), transparent 35%),
        #06060c !important;
    color: #f5f4ff;
    font-family: 'Inter', sans-serif;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainBlockContainer"] {
    max-width: 1450px;
    padding-top: 1.1rem;
    padding-bottom: 2rem;
}
#MainMenu, footer { visibility: hidden; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#101020,#090910);
    border-right: 1px solid rgba(151,130,255,.2);
}
[data-testid="stSidebar"] * { color: #e8e6ff; }
.sidebar-brand {
    font-family: 'Space Grotesk',sans-serif;
    font-size: 20px; font-weight: 700; letter-spacing: 1px;
}
.sidebar-caption {
    font-size: 10px; letter-spacing: 2px;
    color: #a89bff !important; margin-top: 5px;
}
.sidebar-status {
    border: 1px solid rgba(151,130,255,.23);
    border-radius: 12px; background: rgba(24,24,47,.8);
    padding: 12px; font-size: 12px; line-height: 1.9;
    margin: 12px 0; overflow-wrap: anywhere;
}
.topbar {
    display:flex; align-items:center; justify-content:space-between;
    gap:12px; padding:5px 0 20px;
    border-bottom:1px solid rgba(151,130,255,.17);
    margin-bottom:22px;
}
.brand { display:flex; align-items:center; gap:12px; min-width:0; }
.brand-icon {
    width:48px; height:48px; flex-shrink:0;
    display:flex; align-items:center; justify-content:center;
    overflow:hidden; border-radius:12px;
    background:linear-gradient(145deg,#24244b,#101020);
    border:1px solid rgba(155,130,255,.45);
    box-shadow:0 0 25px rgba(109,92,255,.17);
    font-size:26px;
}
.brand-icon img {
    width:100%; height:100%; object-fit:contain;
}
.brand-name {
    font-family:'Space Grotesk',sans-serif;
    font-weight:700; font-size:16px; letter-spacing:1.2px;
}
.brand-sub {
    color:#9998b8; font-size:10px;
    letter-spacing:1.2px; margin-top:4px;
}
.pill {
    border:1px solid rgba(139,132,213,.24);
    border-radius:30px; padding:8px 12px;
    background:rgba(20,20,40,.7); font-size:11px;
    color:#c8c5ec; white-space:nowrap;
}
.hero { text-align:center; padding:15px 0 18px; }
.emblem {
    width:250px; height:250px; max-width:90%;
    margin:0 auto 23px; position:relative;
    display:flex; align-items:center; justify-content:center;
    border-radius:50%;
    background:radial-gradient(circle,#000 0%,#02020b 18%,
        rgba(67,52,160,.48) 32%,rgba(74,111,255,.22) 48%,
        transparent 70%);
    border:1px solid rgba(126,111,255,.35);
    box-shadow:0 0 35px rgba(94,78,255,.25),
        0 0 80px rgba(99,75,255,.16);
}
.emblem:before {
    content:""; position:absolute; inset:23px;
    border-radius:50%; border:3px solid transparent;
    border-top-color:#a78bfa; border-bottom-color:#5b9bff;
    transform:rotate(-24deg);
}
.emblem:after {
    content:""; position:absolute; width:285px; height:86px;
    max-width:112%; border-radius:50%;
    border:3px solid transparent; border-top-color:#d2a6ff;
    border-bottom-color:#4d9dff; transform:rotate(-28deg);
}
.core {
    width:94px; height:94px; border-radius:50%;
    background:radial-gradient(circle at 35% 30%,
        #17152c,#05050c 43%,#000 72%);
    box-shadow:0 0 25px rgba(111,101,255,.95),
        0 0 55px rgba(123,73,255,.75);
    z-index:1;
}
.emblem:has(img) {
    width:min(430px,90%); height:auto; display:block;
    background:transparent; border:none; border-radius:0;
    box-shadow:none; overflow:visible;
}
.emblem:has(img):before, .emblem:has(img):after {
    display:none;
}
.emblem img {
    display:block; width:100%; height:auto; max-height:360px;
    object-fit:contain; object-position:center;
    margin:0 auto; filter:drop-shadow(0 0 22px rgba(110,91,255,.22));
}
.kicker {
    color:#b3a0ff; font-size:10px; letter-spacing:4px;
    font-weight:700; margin-bottom:10px;
}
.hero h1 {
    font-family:'Space Grotesk',sans-serif;
    font-size:clamp(26px,4.2vw,45px);
    letter-spacing:2px; line-height:1.2; margin:0; color:#fff;
}
.hero h1 span {
    background:linear-gradient(100deg,#a4b9ff,#c19bff);
    -webkit-background-clip:text; background-clip:text;
    -webkit-text-fill-color:transparent;
}
.hero-description {
    color:#9999b7; max-width:490px; margin:13px auto 20px;
    line-height:1.8; font-size:13px;
}
.section-label {
    font-size:10px; font-weight:700; letter-spacing:2px;
    color:#aaa6d4; margin:20px 0 12px;
}
.stButton > button, .stLinkButton > a {
    border:1px solid rgba(139,132,213,.25);
    border-radius:12px;
    background:linear-gradient(140deg,rgba(25,25,52,.98),
        rgba(13,14,29,.98));
    color:#eceaff; min-height:44px; font-size:12px;
}
.stButton > button:hover, .stLinkButton > a:hover {
    border-color:#9d8aff;
    background:linear-gradient(140deg,#28234c,#171831);
    color:#fff;
}
[data-testid="stChatMessage"] {
    background:rgba(17,17,35,.8);
    border:1px solid rgba(139,132,213,.18);
    border-radius:15px; padding:14px 16px; margin-bottom:12px;
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
    color:#eeedff; font-size:14px; line-height:1.8;
}
[data-testid="stChatInput"] > div {
    background:#111124 !important;
    border:1px solid rgba(146,128,255,.4) !important;
    border-radius:16px !important;
}
[data-testid="stChatInput"] textarea { color:#fff !important; }
.footer {
    color:#777794; text-align:center; font-size:10px;
    letter-spacing:1.5px; padding:20px 0 10px;
}
@media(max-width:640px) {
    [data-testid="stMainBlockContainer"] {
        padding-left:.8rem; padding-right:.8rem;
    }
    .emblem { width:190px; height:190px; }
    .emblem:after { width:215px; height:65px; }
    .emblem:has(img) { width:min(320px,92%); height:auto; }
    .brand-name { font-size:12px; }
    .brand-sub { font-size:8px; letter-spacing:.8px; }
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

def logo_base64():
    try:
        if LOGO_PATH.is_file():
            return base64.b64encode(LOGO_PATH.read_bytes()).decode()
    except OSError:
        pass
    return None

LOGO = logo_base64()
brand_icon = (
    f'<img src="data:image/png;base64,{LOGO}" alt="Singularity logo">'
    if LOGO else "✦"
)

st.markdown(f"""
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
""", unsafe_allow_html=True)

# =========================================================
# AUTHENTICATION SCREEN
# =========================================================

def auth_screen():
    st.markdown("""
    <div class="hero">
      <div class="kicker">QUNIT INTELLIGENCE SYSTEM</div>
      <h1>YOUR <span>SINGULARITY</span></h1>
      <div class="hero-description">
        Sign in to save your conversations and continue
        exploring across sessions.
      </div>
    </div>
    """, unsafe_allow_html=True)

    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("Supabase settings are missing from Streamlit Secrets.")
        st.stop()

    if st.session_state.auth_notice:
        st.info(st.session_state.auth_notice)
        st.session_state.auth_notice = None

    tab_login, tab_signup = st.tabs(["Sign in", "Create account"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email address", key="login_email")
            password = st.text_input(
                "Password", type="password", key="login_password"
            )
            submitted = st.form_submit_button(
                "Sign in", use_container_width=True
            )

        if submitted:
            if not email.strip() or not password:
                st.warning("Enter your email and password.")
            else:
                try:
                    result = sb.auth.sign_in_with_password({
                        "email": email.strip(),
                        "password": password,
                    })
                    if result.session and result.user:
                        set_logged_in(result.session, result.user)
                        st.rerun()
                    else:
                        st.info("Check your email for any required verification.")
                except Exception:
                    st.error(
                        "Sign-in failed. Check your details and verify "
                        "your email if required."
                    )

    with tab_signup:
        with st.form("signup_form"):
            new_email = st.text_input("Email address", key="signup_email")
            new_password = st.text_input(
                "Create password", type="password", key="signup_password"
            )
            confirm_password = st.text_input(
                "Confirm password", type="password", key="signup_confirm"
            )
            create_account = st.form_submit_button(
                "Create account", use_container_width=True
            )

        if create_account:
            if not new_email.strip():
                st.warning("Enter your email address.")
            elif len(new_password) < 8:
                st.warning("Use a password with at least 8 characters.")
            elif new_password != confirm_password:
                st.warning("The passwords do not match.")
            else:
                try:
                    result = sb.auth.sign_up({
                        "email": new_email.strip(),
                        "password": new_password,
                    })
                    if result.session and result.user:
                        set_logged_in(result.session, result.user)
                        st.success("Account created!")
                        st.rerun()
                    else:
                        st.success(
                            "Account created. Check your email for a "
                            "verification link, then sign in."
                        )
                except Exception:
                    st.error(
                        "Account creation failed. The email may already "
                        "be registered, or the password may not meet "
                        "your Supabase settings."
                    )

    st.divider()
    st.markdown("#### Or continue with Google")

    try:
        oauth = sb.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {"redirect_to": APP_URL},
        })
        oauth_url = getattr(oauth, "url", None)
        if not oauth_url and getattr(oauth, "data", None):
            oauth_url = getattr(oauth.data, "url", None)

        if oauth_url:
            st.link_button(
                "Continue with Google",
                oauth_url,
                use_container_width=True,
            )
        else:
            st.warning("Google sign-in URL was not returned.")
    except Exception:
        st.error(
            "Google sign-in is unavailable. Check the Google provider "
            "and Supabase redirect settings."
        )

    st.caption("Your account protects your own saved conversations.")

if not sb:
    st.error(
        "Supabase is not configured. Check SUPABASE_URL and "
        "SUPABASE_KEY in Streamlit Secrets."
    )
    st.stop()

if not st.session_state.user:
    auth_screen()
    st.stop()

# =========================================================
# CHAT DATABASE HELPERS
# =========================================================

def db_client():
    result = sb.auth.set_session(
        st.session_state.access_token,
        st.session_state.refresh_token,
    )
    if result.session:
        set_logged_in(result.session, result.user)
    return sb

def load_chats():
    client = db_client()
    result = (
        client.table("chats")
        .select("id,title,updated_at")
        .eq("user_id", st.session_state.user["id"])
        .order("updated_at", desc=True)
        .execute()
    )
    return result.data or []

def load_chat(chat_id):
    client = db_client()
    result = (
        client.table("chats")
        .select("id,title,messages")
        .eq("id", chat_id)
        .eq("user_id", st.session_state.user["id"])
        .limit(1)
        .execute()
    )
    if result.data:
        row = result.data[0]
        st.session_state.chat_id = row["id"]
        st.session_state.messages = row.get("messages") or []
        return True
    return False

def save_chat():
    if not st.session_state.messages:
        return

    client = db_client()
    if not st.session_state.chat_id:
        st.session_state.chat_id = str(uuid.uuid4())

    first_user_message = next(
        (
            m["content"] for m in st.session_state.messages
            if m["role"] == "user"
        ),
        "New conversation",
    )
    title = first_user_message.replace("\n", " ").strip()[:60]
    if not title:
        title = "New conversation"

    row = {
        "id": st.session_state.chat_id,
        "user_id": st.session_state.user["id"],
        "title": title,
        "messages": st.session_state.messages,
        "updated_at": "now()",
    }

    # Use a real timestamp instead of a SQL expression string.
    from datetime import datetime, timezone
    row["updated_at"] = datetime.now(timezone.utc).isoformat()

    client.table("chats").upsert(row, on_conflict="id").execute()

def new_chat():
    st.session_state.chat_id = None
    st.session_state.messages = []
    st.session_state.pending_prompt = None

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

    st.caption(f"Signed in as {st.session_state.user['email']}")

    if st.button("＋ New conversation", use_container_width=True):
        new_chat()
        st.rerun()

    st.markdown("### Your saved conversations")

    try:
        chats = load_chats()
        st.session_state.chat_list = chats

        for chat in chats:
            label = (chat.get("title") or "New conversation")[:42]
            if st.button(
                "▸ " + label,
                key="chat_" + chat["id"],
                use_container_width=True,
            ):
                try:
                    if load_chat(chat["id"]):
                        st.rerun()
                except Exception:
                    st.error("Could not load this conversation.")
    except Exception:
        st.warning(
            "Couldn't load chat history. Check the chats table "
            "and its row-level security policies."
        )

    st.divider()
    st.markdown("### Control centre")
    st.markdown(
        f"""
        <div class="sidebar-status">
          <b>AI ENGINE</b><br>OpenRouter Cloud<br><br>
          <b>ACCOUNT</b><br>Signed in<br><br>
          <b>MODEL</b><br>{MODEL}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Clear current conversation", use_container_width=True):
        if st.session_state.chat_id:
            try:
                db_client().table("chats").delete().eq(
                    "id", st.session_state.chat_id
                ).eq(
                    "user_id", st.session_state.user["id"]
                ).execute()
            except Exception:
                st.error("Couldn't delete the saved conversation.")
                st.stop()
        new_chat()
        st.rerun()

    if st.button("Sign out", use_container_width=True):
        try:
            sb.auth.sign_out()
        except Exception:
            pass
        for key in [
            "user", "access_token", "refresh_token",
            "messages", "chat_id", "chat_list",
        ]:
            st.session_state[key] = (
                [] if key in ("messages", "chat_list") else None
            )
        st.session_state.sb_client = None
        st.rerun()

    st.divider()
    st.caption("SINGULARITY AI · BY QUNIT")
    st.caption("Think deeper. Explore further.")

# =========================================================
# HOME SCREEN AND MESSAGES
# =========================================================

if not st.session_state.messages:
    emblem = (
        f'<img src="data:image/png;base64,{LOGO}" '
        'alt="Singularity black hole emblem">'
        if LOGO else '<div class="core"></div>'
    )

    st.markdown(f"""
    <div class="hero">
      <div class="emblem">{emblem}</div>
      <div class="kicker">BEYOND THE KNOWN</div>
      <h1>ENTER THE <span>SINGULARITY</span></h1>
      <div class="hero-description">
        An intelligence for ideas, discovery, and the questions
        that take you beyond the ordinary.
      </div>
    </div>
    <div class="section-label">✦ CHOOSE YOUR EXPLORATION</div>
    """, unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:
        if st.button(
            "◈ Explore a mind-bending science idea",
            use_container_width=True,
        ):
            st.session_state.pending_prompt = (
                "Explain a mind-bending science idea in an engaging, accurate way."
            )
            st.rerun()

        if st.button("⌘ Build something with code", use_container_width=True):
            st.session_state.pending_prompt = (
                "Help me build a useful coding project step by step."
            )
            st.rerun()

    with right:
        if st.button(
            "✧ Invent something extraordinary",
            use_container_width=True,
        ):
            st.session_state.pending_prompt = (
                "Help me develop an original, realistic invention idea."
            )
            st.rerun()

        if st.button("⟡ Explore the universe", use_container_width=True):
            st.session_state.pending_prompt = (
                "Explain a fascinating question about the universe."
            )
            st.rerun()

else:
    st.markdown(
        '<div class="section-label">✦ YOUR CONVERSATION</div>',
        unsafe_allow_html=True,
    )
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# =========================================================
# OPENROUTER CHAT ENGINE
# =========================================================

if not API_KEY:
    st.warning("Add OPENROUTER_API_KEY in Streamlit Secrets.")

prompt = st.chat_input("Ask anything. Explore beyond the known...")

if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if prompt and prompt.strip():
    prompt = prompt.strip()

    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    answer = ""

    with st.chat_message("assistant"):
        if not API_KEY:
            answer = "OpenRouter is not configured. Please contact the app owner."
            st.warning(answer)
        else:
            try:
                api_messages = [
                    {"role": "system", "content": SYSTEM_PROMPT}
                ]
                api_messages.extend(st.session_state.messages[-20:])

                response = requests.post(
                    API_URL,
                    headers={
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": APP_URL,
                        "X-Title": "SINGULARITY AI by QUNIT",
                    },
                    json={
                        "model": MODEL,
                        "messages": api_messages,
                        "temperature": 0.7,
                        "max_tokens": 1200,
                        "stream": False,
                    },
                    timeout=90,
                )

                if not response.ok:
                    try:
                        details = response.json().get(
                            "error", {}
                        ).get("message", "Provider request failed.")
                    except ValueError:
                        details = "Provider request failed."
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
                        for part in answer if isinstance(part, dict)
                    )
                answer = str(answer).strip() or (
                    "I couldn't generate a response. Please try again."
                )
                st.markdown(answer)

            except requests.Timeout:
                answer = "The request timed out. Please try again."
                st.error(answer)
            except requests.RequestException:
                answer = "Could not connect to OpenRouter. Check the connection."
                st.error(answer)
            except Exception as exc:
                answer = f"AI request failed: {str(exc)[:300]}"
                st.error(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
    })

    try:
        save_chat()
    except Exception:
        st.warning(
            "Your AI reply appeared, but the chat could not be saved. "
            "Check your Supabase connection and table policies."
        )

    st.rerun()

st.markdown("""
<div class="footer">
  SINGULARITY AI · CREATED BY QUNIT<br><br>
  THINK DEEPER. BUILD FURTHER. EXPLORE THE UNKNOWN.
</div>
""", unsafe_allow_html=True)


import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import requests
from backend.auth.auth_service import authenticate_user, register_user
from backend.sql.services.chat_history_service import save_message, load_chat_history
from backend.sql.sql_database import init_db

if "db_initialized" not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

st.set_page_config(
    page_title="EKA",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def login_ui():
    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:
        st.markdown(
            '<div class="login-container">',
            unsafe_allow_html=True
        )

        st.markdown("""
<div style="text-align:center; margin-bottom:16px;">
  <div style="display:inline-flex; align-items:center; gap:12px;">
    <div style="width:44px; height:44px; animation:hex-float 4s ease-in-out infinite;">
      <svg width="44" height="44" viewBox="0 0 64 64" fill="none">
        <defs>
          <linearGradient id="hg1l" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#ffffff"/><stop offset="100%" stop-color="#a78bfa"/>
          </linearGradient>
          <linearGradient id="hg2l" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stop-color="#ffffff"/><stop offset="100%" stop-color="#7c3aed"/>
          </linearGradient>
        </defs>
        <polygon class="hex-border" points="32,4 56,18 56,46 32,60 8,46 8,18" fill="none" stroke="url(#hg1l)" stroke-width="1.5" stroke-dasharray="6 3"/>
        <polygon points="32,11 51,22 51,42 32,53 13,42 13,22" fill="url(#hg2l)" opacity="0.15"/>
        <polygon points="32,11 51,22 51,42 32,53 13,42 13,22" fill="none" stroke="url(#hg1l)" stroke-width="1"/>
        <line x1="32" y1="22" x2="32" y2="14" stroke="#c4b5fd" stroke-width="1" opacity="0.7"/>
        <line x1="32" y1="22" x2="22" y2="28" stroke="#c4b5fd" stroke-width="1" opacity="0.7"/>
        <line x1="32" y1="22" x2="42" y2="28" stroke="#c4b5fd" stroke-width="1" opacity="0.7"/>
        <line x1="22" y1="28" x2="22" y2="38" stroke="#a78bfa" stroke-width="1" opacity="0.6"/>
        <line x1="42" y1="28" x2="42" y2="38" stroke="#a78bfa" stroke-width="1" opacity="0.6"/>
        <line x1="22" y1="38" x2="32" y2="44" stroke="#c4b5fd" stroke-width="1" opacity="0.7"/>
        <line x1="42" y1="38" x2="32" y2="44" stroke="#c4b5fd" stroke-width="1" opacity="0.7"/>
        <circle cx="32" cy="22" r="3" fill="#ffffff" opacity="0.9"/>
        <circle class="dp"  cx="22" cy="28" r="2"   fill="#c4b5fd"/>
        <circle class="dp2" cx="42" cy="28" r="2"   fill="#c4b5fd"/>
        <circle class="dp3" cx="22" cy="38" r="2"   fill="#a78bfa"/>
        <circle class="dp"  cx="42" cy="38" r="2"   fill="#a78bfa"/>
        <circle class="dp2" cx="32" cy="44" r="2.5" fill="#c4b5fd"/>
        <circle class="dp3" cx="32" cy="14" r="2"   fill="#ffffff" opacity="0.8"/>
      </svg>
    </div>
    <div style="font-size:38px; font-weight:700; background:linear-gradient(135deg,#ffffff,#e0d7ff,#c4b5fd,#a78bfa); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; letter-spacing:5px; line-height:1;">EKA</div>
  </div>
  <div style="font-size:11px; color:rgba(255,255,255,0.5); letter-spacing:2.5px; margin-top:8px; text-transform:uppercase;">Enterprise Knowledge Assistant</div>
</div>
""", unsafe_allow_html=True)

        option = st.radio(
            "Select Option",
            ["Login", "Sign Up"],
            horizontal=True,
            label_visibility="collapsed"
        )

        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        if option == "Login":
            if st.button("Login", use_container_width=True):
                success, message = authenticate_user(username, password)

                if success:
                    st.session_state.authenticated = True
                    st.session_state.user = username
                    st.session_state.history_loaded = False
                    st.rerun()
                else:
                    st.error(message)

        else:
            if st.button("Create Account", use_container_width=True):
                success, message = register_user(username, password)
                if success:
                    st.success(message)
                else:
                    st.error(message)

        st.markdown('</div>', unsafe_allow_html=True)


st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    color: white !important;
}
            
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] ol,
[data-testid="stChatMessage"] ul,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div {
    color: white !important;
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] strong {
    color: white !important;
}

header[data-testid="stHeader"] {
    display: none;
}

footer {
    display: none;
}
            
.stApp {
    background: linear-gradient(
        135deg,
        #080010,
        #150028,
        #2a0050
    );
}

section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(18px);
}
            
section[data-testid="stSidebar"] * {
    color: white !important;
}

section[data-testid="stSidebar"] .stButton button {
    background: rgba(255,255,255,0.08) !important;
    color: white !important;
    border-radius: 10px;
}

section[data-testid="stSidebar"] .stButton button:hover {
    background: linear-gradient(90deg, #ffffff, #c4b5fd) !important;
    color: white !important;
}

.header {
    text-align: center;
    padding: 14px;
    background: rgba(255,255,255,0.05);
    border-radius: 14px;
}
            
.header h1 {
    font-size: 22px !important;
    color: white !important;
}

.header p {
    font-size: 13px !important;
    color: rgba(255,255,255,0.85) !important;
}

.login-container * {
    color: white !important;
}

.stTextInput input {
    background: rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    border: none !important;
    color: white !important;
}

[data-testid="stBottom"] {
    background: #1a0035 !important;
}

[data-testid="stBottomBlockContainer"] {
    background: #1a0035 !important;
    padding-bottom: 10px !important;
}
[data-testid="stChatInputContainer"] {
    background: #1a0035 !important;
    border-top: none !important;
    padding: 10px 16px !important;
}

[data-testid="stChatInput"] {
    background: transparent !important;
}

[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.08) !important;
    color: black;
    border-radius: 14px !important;
    border: none !important;
}

[data-testid="stChatInput"] button {
    background: linear-gradient(90deg, #ffffff, #c4b5fd) !important;
    border-radius: 10px !important;
}
            
.user-message {
    background: linear-gradient(90deg, #ffffff, #c4b5fd) !important;
    padding: 10px 14px;
    border-radius: 14px;
    margin-left: 35%;
}

.bot-message {
    background: rgba(255,255,255,0.08);
    padding: 10px 14px;
    border-radius: 14px;
    margin-right: 35%;
    color: white !important;
}

.sql-badge {
    background: #6c63ff;
    font-size: 10px;
}

.rag-badge {
    background: #0c9a7;
    font-size: 10px;
}
            
.error-badge {
    background: #ff4d6d;
    font-size: 10px;
}

.source-box {
    background: rgba(255,255,255,0.05);
    border-left: 2px solid #6c63ff;
}
#MainMenu {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    login_ui()
    st.stop()

if "user" in st.session_state and "history_loaded" not in st.session_state:

    chat_history = load_chat_history(
        st.session_state.user,
    )

    st.session_state.messages = [
        {
            "role": chat.role,
            "content": chat.message
        }
        for chat in chat_history
    ]

    st.session_state.history_loaded = True

with st.sidebar:
    if "user" in st.session_state:
        st.markdown(f"👤 Logged in as: **{st.session_state.user}**")
    st.title("Enterprise Knowledge Assistant")
    st.markdown("---")

    st.markdown("### 💡 Try these questions")

    if st.button("Top 5 highest paid employees"):
        st.session_state.messages.append({"role": "user", "content": "Top 5 highest paid employees"})
        st.rerun()

    if st.button("Average salary per department"):
        st.session_state.messages.append({"role": "user", "content": "Average salary per department"})
        st.rerun()

    if st.button("Employees hired after 2022"):
        st.session_state.messages.append({"role": "user", "content": "Employees hired after 2022"})
        st.rerun()
 
    if st.button("Which department pays highest salary"):
        st.session_state.messages.append({"role": "user", "content": "Which department pays highest salary"})
        st.rerun()

    if st.button("What is the leave policy?"):
        st.session_state.messages.append({"role": "user", "content": "What is the leave policy"})
        st.rerun()
    st.markdown("---")


    if st.button(" Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("Enterprise Knowledge Assistant v1.0")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.messages = []
        st.session_state.pop("user", None)
        st.session_state.pop("history_loaded", None)

        st.rerun()

st.markdown("""
<div class="header">
  <div style="display:inline-block; text-align:center;">
    <div style="display:inline-flex; align-items:center; gap:12px;">
      <div style="position:relative; width:44px; height:44px; flex-shrink:0; animation:hex-float 4s ease-in-out infinite;">
        <svg width="44" height="44" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
          <style>
            .hex-border { animation: hex-spin 8s linear infinite; transform-origin: 32px 32px; }
            .dp  { animation: dot-blink 2s ease-in-out infinite; }
            .dp2 { animation: dot-blink 2s ease-in-out infinite 0.5s; }
            .dp3 { animation: dot-blink 2s ease-in-out infinite 1s; }
            @keyframes hex-spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
            @keyframes dot-blink { 0%,100% { opacity:0.3; } 50% { opacity:1; } }
            @keyframes hex-float { 0%,100% { transform:translateY(0px); } 50% { transform:translateY(-5px); } }
          </style>
          <defs>
            <linearGradient id="hg1" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stop-color="#ffffff"/><stop offset="100%" stop-color="#a78bfa"/>
            </linearGradient>
            <linearGradient id="hg2" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stop-color="#ffffff"/><stop offset="100%" stop-color="#7c3aed"/>
            </linearGradient>
          </defs>
          <polygon class="hex-border" points="32,4 56,18 56,46 32,60 8,46 8,18" fill="none" stroke="url(#hg1)" stroke-width="1.5" stroke-dasharray="6 3"/>
          <polygon points="32,11 51,22 51,42 32,53 13,42 13,22" fill="url(#hg2)" opacity="0.15"/>
          <polygon points="32,11 51,22 51,42 32,53 13,42 13,22" fill="none" stroke="url(#hg1)" stroke-width="1"/>
          <line x1="32" y1="22" x2="32" y2="14" stroke="#c4b5fd" stroke-width="1" opacity="0.7"/>
          <line x1="32" y1="22" x2="22" y2="28" stroke="#c4b5fd" stroke-width="1" opacity="0.7"/>
          <line x1="32" y1="22" x2="42" y2="28" stroke="#c4b5fd" stroke-width="1" opacity="0.7"/>
          <line x1="22" y1="28" x2="22" y2="38" stroke="#a78bfa" stroke-width="1" opacity="0.6"/>
          <line x1="42" y1="28" x2="42" y2="38" stroke="#a78bfa" stroke-width="1" opacity="0.6"/>
          <line x1="22" y1="38" x2="32" y2="44" stroke="#c4b5fd" stroke-width="1" opacity="0.7"/>
          <line x1="42" y1="38" x2="32" y2="44" stroke="#c4b5fd" stroke-width="1" opacity="0.7"/>
          <circle cx="32" cy="22" r="3" fill="#ffffff" opacity="0.9"/>
          <circle class="dp"  cx="22" cy="28" r="2"   fill="#c4b5fd"/>
          <circle class="dp2" cx="42" cy="28" r="2"   fill="#c4b5fd"/>
          <circle class="dp3" cx="22" cy="38" r="2"   fill="#a78bfa"/>
          <circle class="dp"  cx="42" cy="38" r="2"   fill="#a78bfa"/>
          <circle class="dp2" cx="32" cy="44" r="2.5" fill="#c4b5fd"/>
          <circle class="dp3" cx="32" cy="14" r="2"   fill="#ffffff" opacity="0.8"/>
        </svg>
      </div>
      <div style="font-size:38px; font-weight:700; background:linear-gradient(135deg,#ffffff,#e0d7ff,#c4b5fd,#a78bfa); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; letter-spacing:5px; line-height:1;">EKA</div>
    </div>
    <div style="font-size:11px; color:rgba(255,255,255,0.5); letter-spacing:2.5px; margin-top:8px; text-transform:uppercase;">Enterprise Knowledge Assistant</div>
  </div>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []


for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        content_html = msg["content"]

        if msg.get("router_method"):
            content_html += f'<div class="router-box">🔀 Routed via: {msg["router_method"]}</div>'

        source_type = msg.get("source_type", "")
        if source_type == "sql":
            content_html += '<span class="sql-badge">🗄️ SQL DATABASE</span>'
        elif source_type == "rag":
            content_html += '<span class="rag-badge">📄 DOCUMENTS</span>'
        elif source_type == "error":
            content_html += '<span class="error-badge">⚠️ ERROR</span>'

        if msg.get("sources"):
            for src in msg["sources"]:
                content_html += f'<div class="source-box">📄 {src}</div>'

        st.markdown(f'<div class="bot-message">{content_html}</div>', unsafe_allow_html=True)

if prompt := st.chat_input("Ask me anything about your data or documents..."):

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    save_message(st.session_state.user, "user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()

        response_placeholder.markdown("Thinking...")

        response = requests.post(
            "http://127.0.0.1:8000/ask",
            json={
                "question": prompt,
                "user": st.session_state.user
          }
        )

        result = response.json()  

        full_response = ""
        for word in result["answer"].split():
            full_response += word + " "
            response_placeholder.markdown(full_response)

        router_method = result.get("router_method", "")
        if router_method:
            st.markdown(
                f'<div class="router-box">🔀 Routed via: {router_method}</div>',
                unsafe_allow_html=True
            )

        source_type = result.get("source_type", "")
        if source_type == "sql":
            st.markdown('<span class="sql-badge">🗄️ SQL DATABASE</span>',
                       unsafe_allow_html=True)
        elif source_type == "rag":
            st.markdown('<span class="rag-badge">📄 DOCUMENTS</span>',
                       unsafe_allow_html=True)
        elif source_type == "error":
            st.markdown('<span class="error-badge">⚠️ ERROR</span>',
                       unsafe_allow_html=True)

        if result.get("sources"):
            with st.expander(f"📎 Sources ({len(result['sources'])})"):
                for src in result["sources"]:
                    st.markdown(f"• {src}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "source_type": result.get("source_type", ""),
        "sources": result.get("sources", []),
        "router_method": result.get("router_method", "")  
    })
    save_message(st.session_state.user, "assistant", result["answer"])

    chat_history = load_chat_history(st.session_state.user)
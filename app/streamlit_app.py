import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import warnings
warnings.filterwarnings("ignore")

import streamlit as st
from backend.router.query_router import route_question
from backend.auth.auth_service import authenticate_user, register_user


st.set_page_config(
    page_title="EKA",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def login_ui():
    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)

        st.markdown('<div class="login-title">🧠 EKA</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Enterprise Knowledge Assistant</div>', unsafe_allow_html=True)

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
                if authenticate_user(username, password):
                    st.session_state.authenticated = True
                    st.session_state.user = username
                    st.rerun()
                else:
                    st.error("Invalid username or password")

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
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f9fafb, #f1f5f9);
        background-attachment: fixed;
    }

    .login-title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .login-subtitle {
        font-size: 14px;
        opacity: 0.8;
        margin-bottom: 25px;
    }

    .stTextInput input {
        border-radius: 12px;
        padding: 12px;
        border: none;
    }

    .stButton button {
        border-radius: 12px;
        height: 48px;
        font-weight: 600;
        background: white;
        color: #333;
    }

    .stRadio > div {
        justify-content: center;
    }

    [data-testid="stDecoration"] {
        display: none;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        flex-direction: row-reverse;
        text-align: right;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
        text-align: right;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background-color: #f0f7ff;
        border-radius: 18px 18px 4px 18px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        padding: 12px 16px;
        margin-left: 20%;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background-color: #ffffff;
        border-radius: 18px 18px 18px 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        padding: 12px 16px;
        margin-right: 20%;
        border: 1px solid #f0f0f0;
    }
    .sql-badge {
        background-color: #1f77b4;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    .rag-badge {
        background-color: #2ca02c;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    .error-badge {
        background-color: #d62728;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    .source-box {
        background-color: #f0f2f6;
        border-left: 3px solid #1f77b4;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 13px;
        margin-top: 8px;
    }
    .router-box {
        background-color: #fafafa;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 11px;
        color: #888;
        margin-bottom: 6px;
        display: inline-block;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    login_ui()
    st.stop()

with st.sidebar:
    if "user" in st.session_state:
        st.markdown(f"👤 Logged in as: **{st.session_state.user}**")
    st.image("https://img.icons8.com/color/96/brain.png", width=80)
    st.title("Enterprise Knowledge Assistant")
    st.markdown("---")

    st.markdown("### How it works")
    st.markdown("""
    - 🗄️ **SQL questions** → Database
    - 📄 **Document questions** → Knowledge Base
    - 🔀 **Router** decides automatically
    """)

    st.markdown("---")
    if st.button("Show top 5 products"):
        st.session_state.messages.append({"role": "user", "content": "Show top 5 products"})
        st.rerun()
    if st.button("How many customers?"):
        st.session_state.messages.append({"role": "user", "content": "How many customers?"})
        st.rerun()
    if st.button("What is leave policy?"):
        st.session_state.messages.append({"role": "user", "content": "What is the leave policy?"})
        st.rerun()
    if st.button("Does the company offer bonuses?"):
        st.session_state.messages.append({"role": "user", "content": "Does the company offer bonuses??"})
        st.rerun()
    st.markdown("---")

    st.markdown("### Router Mode")
    st.markdown("""
    - ⚡ **Keywords** — fast, free
    - 🧠 **LLM** — smart, for edge cases
    """)

    st.markdown("---")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("Enterprise Knowledge Assistant v1.0")
    debug_mode = st.checkbox("🐞 Debug Mode")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.messages = []
        st.session_state.pop("user", None)
        st.rerun()

st.title("🧠 EKA")
st.caption("Ask questions about your database or documents — I'll figure out where to look.")
st.markdown("---")
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.markdown("### 👋 Welcome!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":

            router_method = message.get("router_method", "")
            if router_method:
                st.markdown(
                    f'<div class="router-box">🔀 Routed via: {router_method}</div>',
                    unsafe_allow_html=True
                )

            source_type = message.get("source_type", "")
            if source_type == "sql":
                st.markdown("### 🗄️ SQL Result")
            elif source_type == "rag":
                st.markdown("### 📄 Document Answer")
            elif source_type == "error":
                st.markdown("### ⚠️ Error")
            st.markdown(message["content"])

            if message.get("sources"):
                sources_text = " • ".join(message["sources"])
                st.markdown(
                    f'<div class="source-box">📎 Sources: {sources_text}</div>',
                    unsafe_allow_html=True
                )
        else:
            st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything about your data or documents..."):

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = route_question(prompt)

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

        st.markdown(result["answer"])

        if result.get("sources"):
            for src in result["sources"]:
                st.markdown(
                    f'<div class="source-box">📄 {src}</div>',
                    unsafe_allow_html=True
                )

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "source_type": result.get("source_type", ""),
        "sources": result.get("sources", []),
        "router_method": result.get("router_method", "")  
    })
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warnings
warnings.filterwarnings("ignore")

import streamlit as st
from backend.router.query_router import route_question

st.set_page_config(
    page_title="EKA",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

with st.sidebar:
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
    st.markdown("### Try asking:")
    st.markdown("""
    **SQL:**
    - Show top 5 products
    - How many customers?
    - Top 3 products by revenue

    **RAG:**
    - What is the leave policy?
    - What are employee benefits?
    - Explain the HR guidelines
    """)

    st.markdown("---")
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("Enterprise Knowledge Assistant v1.0")

st.title("🧠 EKA")
st.caption("Ask questions about your database or documents — I'll figure out where to look.")
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):

        if message["role"] == "assistant":

            source_type = message.get("source_type", "")
            if source_type == "sql":
                st.markdown('<span class="sql-badge">🗄️ SQL DATABASE</span>',
                           unsafe_allow_html=True)
            elif source_type == "rag":
                st.markdown('<span class="rag-badge">📄 DOCUMENTS</span>',
                           unsafe_allow_html=True)
            elif source_type == "error":
                st.markdown('<span class="error-badge">⚠️ ERROR</span>',
                           unsafe_allow_html=True)

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
            sources_text = " • ".join(result["sources"])
            st.markdown(
                f'<div class="source-box">📎 Sources: {sources_text}</div>',
                unsafe_allow_html=True
            )

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "source_type": result.get("source_type", ""),
        "sources": result.get("sources", [])
    })
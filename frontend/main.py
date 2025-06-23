import os

import requests
import streamlit as st

# Load external CSS
css_path = "./css/style.css"
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = os.getenv("API_PORT", "80")
API_URL = f"http://{API_HOST}:{API_PORT}/api/ai_agent"


# Professional header
st.markdown(
    """
<div class="header-container">
    <div class="header-title">🛍️ E-Commerce AI Assistant</div>
    <div class="header-subtitle">Intelligent Shopping Companion powered by Advanced AI</div>
</div>
""",
    unsafe_allow_html=True,
)

# Status indicator
st.markdown(
    '<div class="status-badge status-online">🟢 Service Online</div>',
    unsafe_allow_html=True,
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "context" not in st.session_state:
    st.session_state.context = ""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat interface
st.markdown("### 💬 Chat Interface")

# Add welcome message if no messages
if len(st.session_state.messages) == 0:
    st.info(
        "👋 Welcome! Ask me anything about products. I can help you search, browse categories, and find exactly what you're looking for!"
    )

# Display chat messages
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and "tool_info" in message:
            tool_info = message["tool_info"]

        st.markdown(message["content"])

# Chat input
if user_input := st.chat_input("💭 Ask me anything about products..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("🤖 AI is thinking..."):
        try:
            # Prepare API payload
            payload = {
                "user_id": "0",
                "messages": user_input,
            }
            # Nếu đã có session_id thì thêm vào payload
            if "session_id" in st.session_state:
                payload["session_id"] = st.session_state["session_id"]

            response = requests.post(
                API_URL,
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            answer = data.get("messages", "")
            chat_history = data.get("chat_history", [])

            # Nếu response có session_id thì lưu lại cho lần sau
            if "session_id" in data:
                st.session_state["session_id"] = data["session_id"]

            st.session_state.chat_history = chat_history

            assistant_message = {"role": "assistant", "content": answer}
            st.session_state.messages.append(assistant_message)

        except Exception as e:
            st.error(f"Sorry, I encountered an error: {str(e)}")
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "I apologize, but I encountered an error while processing your request. Please try again.",
                }
            )

    st.rerun()

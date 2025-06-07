import json

import langchain
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import ToolMessage

from core.services.chatbot.tools.get_categories_tool import init_get_categories_service
from core.services.chatbot.tools.search_advanced_tool import (
    init_search_advanced_service,
)
from core.services.chatbot.tools.search_basic_tool import init_search_basic_service
from core.services.chatbot.v5.chatbot_service import ChatbotService
from core.services.product.get_categories_service import GetCategoriesService
from core.services.product.search_advanced_service import SearchAdvancedService

load_dotenv()
langchain.debug = True

# Custom CSS for professional styling
st.markdown(
    """
<style>
    .main {
        padding-top: 2rem;
    }
    
    .stApp > header {
        background-color: transparent;
    }
    
    .header-container {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-bottom: 0;
    }
    
    .tool-details {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Enhanced Chat Message Styling */
    .chat-message {
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 10px;
        position: relative;
        animation: fadeIn 0.3s ease-in-out;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .message-user {
        background-color: #f0f7ff;
        border-left: 0;
        border-right: 4px solid #4361ee;
        margin-left: 0.5rem;
        margin-right: 2rem;
        text-align: right;
    }
    
    .message-assistant {
        background-color: #f8f9fa;
        border-left: 4px solid #667eea;
        border-right: 0;
        margin-right: 0.5rem;
        margin-left: 2rem;
        text-align: left;
    }
    
    /* Điều chỉnh header tin nhắn người dùng */
    .message-user .chat-header {
        flex-direction: row-reverse;
        justify-content: flex-start;
    }
    
    .message-user .chat-avatar {
        margin-right: 0;
        margin-left: 0.8rem;
    }
    
    /* Điều chỉnh timestamp */
    .message-user .message-timestamp {
        left: 0.8rem;
        right: auto;
    }
    
    /* Điều chỉnh container tool info */
    .message-user .tool-info-container {
        text-align: left;
    }
    
    .message-timestamp {
        font-size: 0.7rem;
        color: #adb5bd;
        position: absolute;
        top: 0.5rem;
        right: 0.8rem;
    }
    
    .message-content {
        margin-top: 0.5rem;
        line-height: 1.5;
    }
    
    .tool-info-container {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        margin-top: 0.8rem;
        overflow: hidden;
    }
    
    .tool-header {
        display: flex;
        align-items: center;
        padding: 0.6rem 1rem;
        background-color: #e9ecef;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .tool-header:hover {
        background-color: #dee2e6;
    }
    
    .tool-header-icon {
        margin-right: 0.5rem;
        color: #6c757d;
    }
    
    .tool-header-text {
        font-weight: 500;
        color: #495057;
    }
    
    .tool-body {
        padding: 1rem;
        border-top: 1px solid #e9ecef;
    }
    
    .tool-section {
        margin-bottom: 0.8rem;
    }
    
    .tool-section-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #495057;
        margin-bottom: 0.4rem;
    }
    
    .chat-avatar {
        width: 35px;
        height: 35px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        color: white;
        margin-right: 0.8rem;
    }
    
    .avatar-user {
        background-color: #4361ee;
    }
    
    .avatar-assistant {
        background-color: #667eea;
    }
    
    .chat-header {
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .chat-name {
        font-weight: 500;
        color: #212529;
    }
    
    .chat-divider {
        margin: 1.5rem 0;
        text-align: center;
        position: relative;
    }
    
    .chat-divider::before {
        content: "";
        position: absolute;
        top: 50%;
        left: 0;
        right: 0;
        height: 1px;
        background-color: #e9ecef;
        z-index: -1;
    }
    
    .chat-divider-text {
        background-color: white;
        padding: 0 1rem;
        font-size: 0.8rem;
        color: #adb5bd;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def initialize_services():
    """Initialize all services once and cache them"""
    collection_name = "e_commerce_ai"

    search_advanced_service = SearchAdvancedService(collection_name=collection_name)
    get_categories_service = GetCategoriesService(collection_name=collection_name)

    init_search_advanced_service(search_advanced_service)
    init_get_categories_service(get_categories_service)
    init_search_basic_service(search_advanced_service)

    chatbot = ChatbotService(
        llm_model="gemini-2.5-flash-preview-05-20",
        collection_name="e_commerce_ai",
        agent_verbose=False,
    )

    return chatbot


# Initialize services once
chatbot = initialize_services()

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

# Sidebar with information
with st.sidebar:
    st.markdown("### 🎯 Features")
    st.markdown(
        """
    - **Smart Product Search**: Find products using natural language
    - **Category Navigation**: Browse product categories intelligently  
    - **Advanced Filtering**: Detailed search with multiple criteria
    - **Real-time Responses**: Instant AI-powered assistance
    """
    )

    st.markdown("### 📊 Statistics")

    # Calculate statistics
    total_messages = len(st.session_state.messages)

    # Count total tools used correctly
    tools_used_count = 0
    for m in st.session_state.messages:
        if m.get("role") == "assistant" and "tool_info" in m:
            tool_info = m["tool_info"]
            if isinstance(tool_info, list):
                # Multiple tools - count all
                tools_used_count += len(tool_info)
            else:
                # Single tool - count as 1
                tools_used_count += 1

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Messages", total_messages)
    with col2:
        st.metric("Tools Used", tools_used_count)

    st.markdown("---")

    if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.session_state.context = ""
        st.rerun()

    # Add some helpful information
    if total_messages > 0:
        st.markdown("### 💡 Tips")
        st.markdown(
            """
        - Ask about product categories
        - Search for specific items
        - Request advanced filtering
        - Compare products
        """
        )

    # Professional footer
    st.markdown(
        """
    <div class="footer">
        <hr>
        Powered by LangChain & Streamlit | E-Commerce AI Assistant v1.0
    </div>
    """,
        unsafe_allow_html=True,
    )

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

            # Handle both single tool (backward compatibility) and multiple tools
            if isinstance(tool_info, list):
                # Multiple tools - group them in one expander
                tools_count = len(tool_info)
                with st.expander(f"🔧 Tools Used ({tools_count})", expanded=False):
                    for idx, tool in enumerate(tool_info):
                        tool_name = tool.get("tool_name", "Unknown Tool")

                        # Add separator between tools (except for first tool)
                        if idx > 0:
                            st.markdown("---")

                        st.markdown(f"### Tool {idx + 1}: {tool_name}")

                        if tool.get("tool_input"):
                            st.markdown("**Parameters:**")
                            st.json(tool.get("tool_input", {}))

                        if tool.get("tool_output"):
                            st.markdown("**Output:**")
                            output = str(tool.get("tool_output", "No output available"))
                            if len(output) > 1000:
                                output = output[:1000] + "... (truncated)"
                            st.code(output, language="text")
            else:
                # Single tool (backward compatibility)
                tool_name = tool_info.get("tool_name", "Unknown Tool")
                with st.expander(f"🔧 Tool Used: {tool_name}", expanded=False):
                    st.markdown(f"**Tool Name:** `{tool_name}`")

                    if tool_info.get("tool_input"):
                        st.markdown("**Parameters:**")
                        st.json(tool_info.get("tool_input", {}))

                    if tool_info.get("tool_output"):
                        st.markdown("**Output:**")
                        output = str(
                            tool_info.get("tool_output", "No output available")
                        )
                        if len(output) > 1000:
                            output = output[:1000] + "... (truncated)"
                        st.code(output, language="text")

        st.markdown(message["content"])

# Chat input
if user_input := st.chat_input("💭 Ask me anything about products..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    used_tools = []  # Changed from used_tool to used_tools (list)

    with st.spinner("🤖 AI is thinking..."):
        try:
            answer, chat_history = chatbot.run(
                user_input, st.session_state.get("chat_history", [])
            )

            st.session_state.chat_history = chat_history

            # Extract all tool information from chat history
            for message in chat_history:
                if isinstance(message, ToolMessage):
                    tool_info = {
                        "tool_name": message.tool,
                        "tool_input": message.tool_input,
                        "tool_output": message.observation,
                    }
                    # Check if this tool usage is already recorded
                    if tool_info not in used_tools:
                        used_tools.append(tool_info)

            # Add assistant message with all tool info
            assistant_message = {"role": "assistant", "content": answer}

            if used_tools:
                assistant_message["tool_info"] = used_tools  # Now it's a list

            st.session_state.messages.append(assistant_message)

        except Exception as e:
            st.error(f"Sorry, I encountered an error: {str(e)}")
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "I apologize, but I encountered an error while processing your request. Please try again.",
                }
            )

    # Force rerun to update sidebar statistics
    st.rerun()

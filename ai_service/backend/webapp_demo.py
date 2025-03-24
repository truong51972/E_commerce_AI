import streamlit as st
from utils.services.ai_search_with_context import AiSearchWithContext
from utils.services.ai_deep_search import AiDeepSearch
from dotenv import load_dotenv
import langchain

load_dotenv()
langchain.debug = True

# milvus = AiSearchWithContext(collection_name="test_08")
milvus = AiDeepSearch(collection_name="test_08")
st.title("💬 Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "context" not in st.session_state:
    st.session_state.context = ""

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

user_input = st.chat_input("Nhập tin nhắn của bạn...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Đang phản hồi..."):
        output = milvus.search(text=user_input, user_context=st.session_state.context)
        thinking_process_1 = output.get("thinking_1", "None")
        extracted_docs = output.get("docs", "None")
        thinking_process_2 = output.get("thinking_2", "None")
        context_info = output["context"]
        answer = output["answer"]

    st.session_state.context = context_info

    with st.chat_message("assistant"):
        st.markdown(f"""
        <details>
            <summary>Thinking...</summary>
            <p style='color:gray; font-size: 16px;'>{thinking_process_1}</p>
            <details>
                <summary>Extracted Documents</summary>
                <p style='color:gray; font-size: 14px;'>{extracted_docs}</p>
                <hr>
            </details>
            <p style='color:gray; font-size: 16px;'>{thinking_process_2}</p>
            <hr>
        </details>
        """, unsafe_allow_html=True)

        st.markdown(answer)  # Chỉ Markdown cho phần nội dung chính (hỗ trợ link)


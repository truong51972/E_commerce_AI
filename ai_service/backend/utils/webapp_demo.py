# run command: streamlit run webapp_demo.py --server.port 8080 --server.address 0.0.0.0

import streamlit as st
from milvus_action import Milvus_Action
from dotenv import load_dotenv

load_dotenv()


# milvus = Milvus_Action(collection_name="clothes_gemini")
milvus = Milvus_Action(collection_name="test_05")
st.title("💬 Chatbot")

# Lưu lịch sử hội thoại trong session
if "messages" not in st.session_state:
    st.session_state.messages = []

if "context" not in st.session_state:
    st.session_state.context = ""

# Hiển thị lịch sử hội thoại
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Ô nhập tin nhắn
user_input = st.chat_input("Nhập tin nhắn của bạn...")

if user_input:
    # Hiển thị tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Gửi tin nhắn đến OpenAI API
    with st.spinner("Đang phản hồi..."):
        output = milvus.AI_search_with_context(
            text=user_input, user_context=st.session_state.context
        )
        print(output)
        st.session_state.context = output["context"]
        bot_reply = output["answer"]

    # Hiển thị tin nhắn từ chatbot
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)

import streamlit as st
from utils.services.ai_search_with_context import AiSearchWithContext
# from utils.services.ai_deep_search import AiDeepSearch
from utils.services.ai_deep_search_v2 import AiDeepSearch
from dotenv import load_dotenv
import langchain

load_dotenv()
milvus = AiDeepSearch(collection_name="e_commerce_ai")
st.title("💬 Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "context" not in st.session_state:
    st.session_state.context = ""

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)


if user_input := st.chat_input("Nhập tin nhắn của bạn..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Đang phản hồi..."):
        # output = milvus.search(user_input=user_input, context=st.session_state.context) #v1

        output = milvus.search(user_input=user_input, history=st.session_state.messages[-11:-1]) #v2
        thinking_process_1 = output.get("thinking_1", "None")
        keywords = output.get("keywords", "None")
        extracted_docs = output.get("docs", "None")
        thinking_process_2 = output.get("thinking_2", "None")
        answer = output.get("answer", "None")

        st.session_state.context = output["context"]
        st.session_state.messages.append({"role": "assistant", "content": answer})

    with st.chat_message("assistant"):
        st.markdown(f"""
        <details>
            <summary>Thinking...</summary>
            <p style='color:gray; font-size: 16px;'>{thinking_process_1}</p>
            <p style='color:gray; font-size: 16px;'>Keywords: {keywords}</p>
            <details>
                <summary>Extracted Documents</summary>
                <p style='color:gray; font-size: 14px;'>{extracted_docs}</p>
                <hr>
            </details>
            <p style='color:gray; font-size: 16px;'>{thinking_process_2}</p>
            <hr>
        </details>
        """, unsafe_allow_html=True)

        st.markdown(answer)
    


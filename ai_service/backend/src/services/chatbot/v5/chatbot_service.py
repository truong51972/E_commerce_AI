# src.services.product.v5.chatbot
import logging

import langchain
from dotenv import load_dotenv

from src.base.service.base_chatbot_service import BaseChatbotService
from src.services.common.tools.get_categories_tool import GetCategoriesTool
from src.services.common.tools.make_order_tool import make_order_tool
from src.services.common.tools.search_basic_tool import SearchBasicTool
from src.services.product.get_categories_service import GetCategoriesService
from src.services.product.search_advanced_service import SearchAdvancedService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(funcName)s: %(message)s",
)

prompt = None
with open("src/services/chatbot/v5/prompts/chat_bot_service_prompt_v3.md", "r") as f:
    prompt = f.read()


class ChatbotService(BaseChatbotService):
    llm_model: str = "gemini-2.5-flash-preview-05-20"
    # llm_model: str = "gemini-2.0-flash-lite"
    agent_prompt: str = prompt
    llm_temperature: float = 0.2
    agent_verbose: bool = False
    return_intermediate_steps: bool = False


if __name__ == "__main__":
    import time

    load_dotenv()
    langchain.debug = True

    collection_name = "e_commerce_ai"

    search_advanced_service = SearchAdvancedService(collection_name=collection_name)
    get_categories_service = GetCategoriesService(collection_name=collection_name)

    chat_bot_service = ChatbotService(
        tools=[
            SearchBasicTool(search_advanced_service=search_advanced_service),
            # SearchAdvancedTool(search_advanced_service=search_advanced_service),
            GetCategoriesTool(get_categories_service=get_categories_service),
            make_order_tool,
        ],
    )
    chat_history = []

    # Example usage

    list_conversation = [
        # "bên mày bán những gì",
        # "thời trang nam thì sao",
        # "áo thì có loại nào",
        # "gợi ý cho tôi vài cái áo polo",
        # "còn mẫu khác không",  # chưa giải quyết được kịch bản này
        "tao muốn mua giày nữ"
    ]

    # Giả lập lịch sử trò chuyện
    context_window_size = 10
    for user_input in list_conversation:
        print(f"\nBạn: {user_input}")
        # Gọi hàm run để lấy câu trả lời từ agent
        answer, chat_history = chat_bot_service.run(
            user_input, chat_history[-context_window_size:]
        )
        # show chat history
        # for message in chat_history:
        #     if isinstance(message, str):
        #         print(f"Chat history: {message}")
        #     elif isinstance(message, list):
        #         for msg in message:
        #             print(f"Chat history: {msg.content}")
        #     else:
        #         print(f"Chat history: {message.content}")

        print(f"\nTrợ lý: {answer}")
        time.sleep(2)

    while True:
        user_input = input("\nBạn: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        answer, chat_history = chat_bot_service.run(
            user_input, chat_history[-context_window_size:]
        )
        # print(chat_history)
        print(f"\nTrợ lý: {answer}")

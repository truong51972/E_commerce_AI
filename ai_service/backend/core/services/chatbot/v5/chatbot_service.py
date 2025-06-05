# core.services.product.v5.chatbot
import logging
from typing import List, Optional

from dotenv import load_dotenv

from core.base.base_ai_agent import BaseAiAgent
from core.services.chatbot.tools.search_advanced_tool import (
    init_search_advanced_service,
    search_advanced_tool,
)
from core.services.chatbot.tools.get_categories_tool import (
    get_categories_tool,
    init_get_categories_service,
)
from core.services.chatbot.tools.make_order_tool import make_order_tool
from core.services.product.get_categories_service import GetCategoriesService
from core.services.product.search_advanced_service import SearchAdvancedService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(funcName)s: %(message)s",
)

prompt = None
with open("core/services/chatbot/v5/prompts/chat_bot_service_prompt_v2.md", "r") as f:
    prompt = f.read()


class ChatbotService(BaseAiAgent):
    llm_model: str = "gemini-2.0-flash-lite"
    agent_prompt: str = prompt
    tools: Optional[List[object]] = [
        search_advanced_tool,
        make_order_tool,
        get_categories_tool,
    ]
    llm_temperature: float = 0.1
    agent_verbose: bool = True
    return_intermediate_steps: bool = True


if __name__ == "__main__":
    import time

    load_dotenv()

    collection_name = "e_commerce_ai"

    search_advanced_service = SearchAdvancedService(collection_name=collection_name)
    get_categories_service = GetCategoriesService(collection_name=collection_name)

    init_search_advanced_service(search_advanced_service)
    init_get_categories_service(get_categories_service)

    chat_bot_service = ChatbotService()
    chat_history = []

    # Example usage

    list_conversation = [
        "bên mày bán những gì",
        "thời trang nam thì sao",
        "áo thì có loại nào",
        "gợi ý cho tôi vài cái áo polo",
        "còn mẫu khác không",  # chưa giải quyết được kịch bản này
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

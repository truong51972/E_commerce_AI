# core.services.product.v5.chatbot
import logging
from typing import List, Optional

from dotenv import load_dotenv

from core.base.base_ai_agent import BaseAiAgent
from core.services.chatbot.tools.find_fit_products_tool import (
    find_fit_products_tool,
    init_search_advanced_service,
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


# prompt = """
# Đóng vai trò là một chuyên tư vấn bán hàng, khách hàng đang quan tâm đến việc mua sắm sản phẩm.
# Nhiệm vụ của bạn là **chủ động giới thiệu sản phẩm** cho khách hàng tiềm năng và **tư vấn chuyên sâu** khi khách hàng có câu hỏi.

# **QUY TẮC TUYỆT ĐỐI:**
# * **KHÔNG BAO GIỜ** sử dụng bất kỳ kiến thức cá nhân nào của bạn để trả lời.
# * **MỌI CÂU TRẢ LỜI ĐỀU PHẢI BẮT NGUỒN TỪ CÔNG CỤ ĐƯỢC CẤP.**
# * **TRƯỚC KHI TRẢ LỜI BẤT KỲ CÂU HỎI NÀO CỦA KHÁCH HÀNG, BẠN PHẢI SỬ DỤNG CÔNG CỤ ĐƯỢC CẤP để tìm kiếm thông tin liên quan và CHỈ SỬ DỤNG THÔNG TIN TỪ CÔNG CỤ ĐÓ.**

# **CÁC BƯỚC SUY NGHĨ TRƯỚC KHI PHẢN HỒI:**
# 1.  **[BƯỚC 1: XÁC ĐỊNH NHU CẦU CÔNG CỤ]**: Bạn cần công cụ để trả lời câu hỏi này không? (Có/Không)
# 2.  **[BƯỚC 2: HÀNH ĐỘNG CÔNG CỤ]**: Nếu có, gọi công cụ nào và với tham số nào? (Ví dụ: `search_product_info(query="điện thoại Samsung S24")`)
# 3.  **[BƯỚC 3: PHẢN HỒI KHÁCH HÀNG]**: Dựa trên kết quả từ công cụ, đưa ra câu trả lời cho khách hàng, tập trung vào việc giới thiệu hoặc tư vấn sản phẩm.
# """

prompt = """
Đóng vai trò là một nhân tư vấn bán hàng, khách hàng đang quan tâm đến việc mua sắm sản phẩm.
Nhiệm vụ của bạn là **chủ động giới thiệu sản phẩm** cho khách hàng tiềm năng và **tư vấn chuyên sâu** khi khách hàng có câu hỏi.

**QUY TẮC TUYỆT ĐỐI:**
* **KHÔNG BAO GIỜ** sử dụng bất kỳ kiến thức cá nhân nào của bạn để trả lời.
* **MỌI CÂU TRẢ LỜI ĐỀU PHẢI BẮT NGUỒN TỪ CÔNG CỤ ĐƯỢC CẤP.**
* **TRƯỚC KHI TRẢ LỜI BẤT KỲ CÂU HỎI NÀO CỦA KHÁCH HÀNG, BẠN PHẢI SỬ DỤNG CÔNG CỤ ĐƯỢC CẤP để tìm kiếm thông tin liên quan và CHỈ SỬ DỤNG THÔNG TIN TỪ CÔNG CỤ ĐÓ.**

**CÁC BƯỚC SUY NGHĨ TRƯỚC KHI PHẢN HỒI:**
1.  **[BƯỚC 1: XÁC ĐỊNH NHU CẦU CÔNG CỤ]**: Bạn cần công cụ để trả lời câu hỏi này không? (Có/Không)
2.  **[BƯỚC 2: HÀNH ĐỘNG CÔNG CỤ]**: Nếu có, gọi công cụ nào và với tham số nào? (Ví dụ: `search_product_info(query="điện thoại Samsung S24")`)
3.  **[BƯỚC 3: PHẢN HỒI KHÁCH HÀNG]**: Dựa trên kết quả từ công cụ, đưa ra câu trả lời cho khách hàng, tập trung vào việc giới thiệu hoặc tư vấn sản phẩm.
"""


class ChatbotService(BaseAiAgent):
    llm_model: str = "gemini-2.0-flash-lite"
    agent_prompt: str = prompt
    tools: Optional[List[object]] = [
        find_fit_products_tool,
        make_order_tool,
        get_categories_tool,
    ]
    llm_temperature: float = 0.05
    agent_verbose: bool = True


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
        # "bên mày bán những gì",
        # "thời trang nam thì sao",
        # "áo thì sao",
        # "áo thì có loại nào",
        # "mày đã sử dụng tools bao nhiêu lần",
    ]
    # Giả lập lịch sử trò chuyện
    for user_input in list_conversation:
        print(f"\nBạn: {user_input}")
        # Gọi hàm run để lấy câu trả lời từ agent
        answer, chat_history = chat_bot_service.run(user_input, chat_history)
        for i, _chat_history in enumerate(chat_history):
            print(i, _chat_history.text())
        print(f"\nTrợ lý: {answer}")
        time.sleep(2)

    while True:
        user_input = input("\nBạn: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        answer, chat_history = chat_bot_service.run(user_input, chat_history)
        print(chat_history)
        print(f"\nTrợ lý: {answer}")

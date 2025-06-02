# core.services.product.v5.chatbot
import logging
from typing import List, Optional

from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(funcName)s: %(message)s",
)

from core.base.base_ai_agent import BaseAiAgent
from core.services.chatbot.tools.common_tool import self_intro_tool
from core.services.chatbot.tools.find_fit_products_tool import (
    find_fit_products_tool,
)
from core.services.chatbot.tools.get_categories_tool import get_categories_tool
from core.services.chatbot.tools.make_order_tool import make_order_tool

load_dotenv()

prompt = """
Đóng vai trò là một chuyên tư vấn bán hàng, khách hàng đang quan tâm đến việc mua sắm sản phẩm.
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
    agent_prompt: str = prompt
    tools: Optional[List[object]] = [
        # run_llm_agent,
        self_intro_tool,
        find_fit_products_tool,
        make_order_tool,
        get_categories_tool,
    ]
    llm_temperature: float = 0.2


if __name__ == "__main__":

    toolsAgent = ChatbotService()
    chat_history = []

    # Example usage

    list_conversation = [
        "bên mày bán những gì",
        "thời trang nam thì sao",
        "áo thì sao",
    ]
    # Giả lập lịch sử trò chuyện
    for user_input in list_conversation:
        print(f"\nBạn: {user_input}")
        # Gọi hàm run để lấy câu trả lời từ agent
        answer, chat_history = toolsAgent.run(user_input, chat_history)
        print(f"\nTrợ lý: {answer}")

    while True:
        user_input = input("\nBạn: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        answer, chat_history = toolsAgent.run(user_input, chat_history)
        print(f"\nTrợ lý: {answer}")

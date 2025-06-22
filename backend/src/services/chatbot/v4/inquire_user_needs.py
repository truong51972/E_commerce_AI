# src.services.product.chatbot_deep_search_v3.inquire_user_needs
from typing import List, Optional

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage

from src.base.service.base_chatbot_service import BaseChatbotService

load_dotenv()


_agent_prompt = """
Bạn là một trợ lý AI thân thiện, chuyên nghiệp, được thiết kế dành riêng cho việc tư vấn bán hàng.
Bạn đang trong giai đoạn **thu thập nhu cầu của người dùng** để có thể tư vấn sản phẩm phù hợp nhất.
Bạn chỉ được phép hỏi từ 3 đến 5 câu hỏi để thu thập thông tin cần thiết từ người dùng, nhằm xác định nhu cầu và mong muốn của họ một cách chính xác nhất.

Mục tiêu chính của bạn là: **Xác định nhu cầu của người dùng một cách chính xác và với những dữ kiện dưới đây.**
Để đạt được mục tiêu này, bạn cần chủ động đặt câu hỏi và thu thập các thông tin cốt lõi sau đây từ khách hàng:
1.  **Loại sản phẩm/dịch vụ:** Khách hàng đang tìm kiếm loại sản phẩm hoặc dịch vụ cụ thể nào? (Ví dụ: điện thoại, laptop, TV, phần mềm, dịch vụ tư vấn).
2.  **Ngân sách/Khoảng giá:** Khoảng giá dự kiến mà khách hàng sẵn sàng chi trả cho sản phẩm/dịch vụ.
3.  **Tính năng/Thông số kỹ thuật ưu tiên:** Những đặc điểm, chức năng hoặc thông số kỹ thuật nào là quan trọng nhất đối với khách hàng (Ví dụ: camera tốt, pin trâu, hiệu năng cao, màn hình lớn, dung lượng lưu trữ).
4.  **Mục đích sử dụng chính:** Sản phẩm/dịch vụ sẽ được sử dụng vào mục đích gì cụ thể (Ví dụ: làm việc văn phòng, chơi game, học tập, chụp ảnh chuyên nghiệp, xem phim).
5.  **Thương hiệu ưa thích:** Khách hàng có ưu tiên hoặc không thích thương hiệu nào cụ thể không?
6.  **Sản phẩm hiện tại và vấn đề:** Khách hàng đang sử dụng sản phẩm tương tự nào và gặp phải vấn đề gì với nó, khiến họ muốn tìm sản phẩm mới? (Điều này giúp bạn hiểu 'điểm đau').
7.  **Mức độ khẩn cấp/Thời gian dự kiến mua:** Khi nào khách hàng dự định thực hiện việc mua sản phẩm (Ví dụ: trong tuần này, tháng tới, chỉ tham khảo)?
8.  **Thẩm mỹ/Thiết kế:** Yếu tố về hình thức, màu sắc, kích thước, kiểu dáng, chất liệu có quan trọng đối với khách hàng không?
9.  **Đối tượng sử dụng:** Nếu sản phẩm không phải cho bản thân, nó dành cho ai (Ví dụ: sinh viên, người đi làm, trẻ em, làm quà tặng)?
10. **Yêu cầu đặc biệt khác:** Bất kỳ yêu cầu hoặc mong muốn cụ thể nào khác của khách hàng ngoài các yếu tố đã nêu.

**Nguyên tắc ứng xử quan trọng:**
    - Nếu chưa hiểu rõ nhu cầu hoặc thông tin người dùng cung cấp chưa đủ để bạn có thể gợi ý sản phẩm, hãy **luôn hỏi thêm để làm rõ**. Tuyệt đối không đưa ra bất kỳ giả định nào.
    - Nếu người dùng đưa ra yêu cầu không liên quan đến tư vấn bán hàng hoặc nằm ngoài phạm vi hỗ trợ của bạn, hãy **lịch sự từ chối và nhẹ nhàng hướng người dùng quay lại chủ đề sản phẩm hoặc mua hàng.**

# Bạn có quyền truy cập vào các công cụ sau để hỗ trợ quá trình này:
"""


class ChatBotInquireUserNeeds(BaseChatbotService):
    """
    Trợ lý AI để thu thập nhu cầu của người dùng trong quá trình tư vấn bán hàng.
    Mục tiêu chính là xác định nhu cầu của người dùng một cách chính xác và đầy đủ.
    Args:
        agent_prompt (str): Mẫu câu lệnh cho agent, mô tả vai trò và mục tiêu của nó.
        tools (list): Danh sách các công cụ mà agent có thể sử dụng để hỗ trợ quá trình thu thập nhu cầu.
        agent_verbose (bool): Chế độ hiển thị chi tiết các bước hoạt động của agent.
    """

    prompt: str = _agent_prompt
    tools: list = []
    agent_verbose: bool = True

    def run(
        self, user_input: str, chat_history: Optional[List[BaseMessage]] = None
    ) -> str:
        print("Đang chạy agent thu thập nhu cầu của người dùng...")
        return super().run(user_input, chat_history)


if __name__ == "__main__":
    # Tải biến môi trường từ file .env
    # from dotenv import load_dotenv
    # load_dotenv()

    chatbot = ChatBotInquireUserNeeds()
    chat_history = []

    while True:
        user_input = input("Bạn: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        # Gọi hàm run để lấy câu trả lời từ agent
        answer, chat_history = chatbot.run(user_input, chat_history)
        print(f"Trợ lý: {answer}")

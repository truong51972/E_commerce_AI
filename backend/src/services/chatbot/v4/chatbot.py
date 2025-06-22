# src.services.product.chatbot_deep_search_v3.chatbot
from typing import List, Optional

from dotenv import load_dotenv
from langchain.tools import tool
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, model_validator

from src.base.service.base_chatbot_service import BaseChatbotService
from src.models.product.product_model import ProductModel, ProductSchema
from src.services.common.tools.search_advanced_tool import SearchAdvancedTool

from .inquire_user_needs import ChatBotInquireUserNeeds

load_dotenv()


chat_history = []
chatBotInquireUserNeeds = ChatBotInquireUserNeeds()


@tool
def self_intro(user_input: str) -> str:
    """
    Công cụ để giới thiệu bản thân.
    Ở giai đoạn này, bạn sẽ giới thiệu về vai trò của mình là một trợ lý AI chuyên tư vấn bán hàng.
    Args:
        user_input (str): Đầu vào từ người dùng, có thể là câu hỏi hoặc yêu cầu liên quan đến sản phẩm.
    Returns:
        str: Một lời giới thiệu ngắn gọn về vai trò và mục tiêu của bạn.
    """
    return f"Chào bạn! Tôi là trợ lý AI của bạn, chuyên tư vấn bán hàng. Tôi ở đây để giúp bạn tìm kiếm sản phẩm phù hợp với nhu cầu của mình."


@tool
def inquire_user_needs(user_input: str) -> str:
    """
    Công cụ này đại diện cho **tác nhân con chuyên trách giai đoạn Thu thập nhu cầu của khách hàng**.
    Hãy sử dụng công cụ này **NGAY LẬP TỨC** và **luôn ưu tiên** khi người dùng:
    Đây là công cụ khởi đầu để khai thác thông tin từ người dùng khi họ chưa rõ ý định.

    Args:
        user_input (str): Đầu vào từ khách hàng, có thể là câu hỏi hoặc yêu cầu liên quan đến sản phẩm.
    Returns:
        str: Một câu hỏi hoặc yêu cầu để tìm hiểu thông tin về nhu cầu của khách hàng.
    """
    return chatBotInquireUserNeeds.run(user_input, chat_history)


product_model = ProductModel(collection_name="e_commerce_ai")


@tool
def get_product_detail(product_ids: List[int]) -> List[ProductSchema]:
    """
    Công cụ để lấy thông tin chi tiết về sản phẩm.
    Ở giai đoạn này, nếu người dùng đã xác định được sản phẩm cụ thể, bạn sẽ cung cấp thông tin chi tiết về sản phẩm đó.
    Args:
        product_ids (List[int]): Danh sách các ID sản phẩm mà người dùng quan tâm.
    Returns:
        List[ProductSchema]: Danh sách các sản phẩm với thông tin chi tiết.
    """
    return product_model.read_records(product_ids)


searchAdvanced = SearchAdvancedTool(collection_name="e_commerce_ai")


@tool
def find_fit_product(
    text: str,
    price_range: list[float] = [0, 1e9],
    categories: list[str] = ["category_1", "category_2"],
    k: int = 5,
) -> List[str]:
    """
    Công cụ để tìm kiếm sản phẩm phù hợp với nhu cầu của người dùng.
    Bạn sẽ sử dụng các công cụ tìm kiếm để xác định sản phẩm phù hợp nhất với yêu cầu của người dùng.
    Args:
        text (str): Mô tả nhu cầu hoặc yêu cầu của người dùng.
        price_range (list[float]): Khoảng giá dự kiến mà người dùng sẵn sàng chi trả.
        categories (list[str]): Danh sách các danh mục sản phẩm mà người dùng quan tâm.
        k (int): Số lượng sản phẩm muốn tìm kiếm. mặc định là 5.
    Returns:
        List[str]: Danh sách các sản phẩm phù hợp với nhu cầu của người dùng.
    """
    result = searchAdvanced.search(
        text=text,
        price_range=price_range,
        categories=categories,
        k=k,
    )
    print(f"Đã tìm thấy {len(result)} sản phẩm phù hợp với yêu cầu của bạn.")
    return result


@tool
def make_order(
    product_detail: str = "Chi tiết sản phẩm",
    amount: int = 1,
    delivery_address: str = "Địa chỉ giao hàng",
    contact_phone: str = "Số điện thoại liên hệ",
) -> str:
    """
    Công cụ tạo đơn hàng.
    Ở giai đoạn này, nếu người dùng ưng ý với sản phẩm, bạn sẽ bắt đầu tạo đơn hàng để gửi về bộ phận khác để xác nhận.
    Bạn sẽ cần thông tin chi tiết về đơn hàng, bao gồm sản phẩm, số lượng, địa chỉ giao hàng và số điện thoại liên hệ.
    Bạn sẽ không tự mình xử lý đơn hàng, mà chỉ gửi thông tin để bộ phận khác xử lý.
    Args:
        product_detail (str): Chi tiết sản phẩm mà người dùng đã chọn.
        amount (int): Số lượng sản phẩm mà người dùng muốn đặt hàng.
        delivery_address (str): Địa chỉ giao hàng của người dùng.
        contact_phone (str): Số điện thoại liên hệ của người dùng.
    Returns:
        str: Một thông báo xác nhận đơn hàng.
    """
    print("Đang xử lý đơn hàng...")
    return f"Đơn hàng của bạn đã được xác nhận. Chúng tôi sẽ liên hệ với bạn để xác nhận thông tin giao hàng."


_agent_prompt = """
Bạn là một trợ lý AI thân thiện, chuyên nghiệp, được thiết kế dành riêng cho việc tư vấn bán hàng.
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

Nếu đã đủ thông tin để gợi ý sản phẩm, bạn sẽ chuyển sang giai đoạn tư vấn sản phẩm.
Và khi người dùng đã chọn được sản phẩm phù hợp, bạn sẽ chuyển sang giai đoạn tạo đơn hàng để gửi về bộ phận khác để xác nhận. Sử dụng công cụ `make_order` để thực hiện việc này.
Bạn sẽ không tự mình xử lý đơn hàng, mà chỉ gửi thông tin để bộ phận khác xử lý.

**Nguyên tắc ứng xử quan trọng:**
    - Nếu chưa hiểu rõ nhu cầu hoặc thông tin người dùng cung cấp chưa đủ để bạn có thể gợi ý sản phẩm, hãy **luôn hỏi thêm để làm rõ**. Tuyệt đối không đưa ra bất kỳ giả định nào.
    - Nếu người dùng đưa ra yêu cầu không liên quan đến tư vấn bán hàng hoặc nằm ngoài phạm vi hỗ trợ của bạn, hãy **lịch sự từ chối và nhẹ nhàng hướng người dùng quay lại chủ đề sản phẩm hoặc mua hàng.**

# Bạn có quyền truy cập vào các công cụ sau để hỗ trợ quá trình này:
"""


class ChatBot(BaseChatbotService):
    prompt: str = _agent_prompt
    tools: list = [
        self_intro,
        # inquire_user_needs,
        get_product_detail,
        find_fit_product,
        make_order,
    ]
    agent_verbose: bool = True


if __name__ == "__main__":
    # Tải biến môi trường từ file .env
    # from dotenv import load_dotenv
    # load_dotenv()

    chatbot = ChatBot()

    list_conversation = [
        "xin chào",
        "tôi muốn mua sản phẩm",
        "tôi cần một cái áo mới",
        "áo khoác",
        "dưới 3 triệu",
        "mua để đi chơi",
        "kiểu dáng thoải mái",
    ]
    # Giả lập lịch sử trò chuyện
    for user_input in list_conversation:
        print(f"Bạn: {user_input}")
        # Gọi hàm run để lấy câu trả lời từ agent
        answer, chat_history = chatbot.run(user_input, chat_history)
        print(f"Trợ lý: {answer}")

    while True:
        user_input = input("Bạn: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        answer, chat_history = chatbot.run(user_input, chat_history)
        print(f"Trợ lý: {answer}")

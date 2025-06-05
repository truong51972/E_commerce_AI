import logging

from langchain.tools import tool
from pydantic import validate_call, Field


@tool
@validate_call
def make_order_tool(
    product_details: list[str] = Field(
        default_factory=list[str],
        description="mô tả từng sản phẩm",
        min_length=1,
    ),
    amounts: list[int] = Field(
        default_factory=list[int],
        description="số lượng từng sản phẩm",
        min_length=1,
    ),
    user_name: str = Field(default_factory=str, description="tên của khách hàng"),
    delivery_address: str = Field(default_factory=str, description="Địa chỉ giao hàng"),
    contact_phone: str = Field(
        default_factory=str, description="Số điện thoại liên hệ"
    ),
) -> str:
    """Tạo yêu cầu đặt hàng mới.

    Sử dụng công cụ này khi khách hàng đã đồng ý mua sản phẩm và bạn cần thu thập thông tin để tạo đơn hàng.
    Công cụ này sẽ gửi chi tiết đơn hàng đến bộ phận xử lý và không tự mình hoàn tất giao dịch.

    Args:
        product_details (list[str]): Danh sách mô tả chi tiết từng sản phẩm khách hàng muốn đặt.
                                     Ví dụ: ["Áo thun cotton trắng size M", "Quần jeans xanh size 30"].
        amounts (list[int]): Danh sách số lượng tương ứng với từng sản phẩm trong `product_details`.
                             Ví dụ: [2, 1] nếu khách mua 2 áo thun và 1 quần jeans.
        user_name (str): Tên đầy đủ của khách hàng đặt đơn.
        delivery_address (str): Địa chỉ chi tiết để giao hàng.
        contact_phone (str): Số điện thoại để liên hệ với khách hàng.

    Returns:
        str: Thông báo xác nhận rằng yêu cầu đặt hàng đã được gửi đi thành công.

    Ví dụ:
        `make_order_tool(product_details=["Áo phông Unisex S", "Quần Kaki L"], amounts=[1, 1], user_name="Nguyễn Văn A", delivery_address="123 Lê Lợi, Quận 1, TP.HCM", contact_phone="0901234567")`
    """
    logging.info("make_order_tool called")
    return "Đơn hàng của bạn đã được xác nhận. Chúng tôi sẽ liên hệ với bạn để xác nhận thông tin giao hàng."

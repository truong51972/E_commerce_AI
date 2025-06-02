import logging

from langchain.tools import tool


@tool
def make_order_tool(
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
    logging.info("make_order_tool called")
    return f"Đơn hàng của bạn đã được xác nhận. Chúng tôi sẽ liên hệ với bạn để xác nhận thông tin giao hàng."

import logging
from typing import List, Optional

from dotenv import load_dotenv
from langchain.tools import tool
from pydantic import validate_call

from core.services.product.search_advanced_service import SearchAdvancedService

load_dotenv()

__searchAdvanced = None


@validate_call
def init_search_basic_service(searchAdvancedService: SearchAdvancedService):
    global __searchAdvanced
    __searchAdvanced = searchAdvancedService


@tool
def search_basic_tool(
    description: str,
    price_range: list[float] = [0, 1e9],
    product_amount: int = 5,
    product_offset: int = 0,
    excluded_product_names: Optional[List[str]] = None,
) -> List[str]:
    """Tìm kiếm sản phẩm phù hợp với nhu cầu người dùng.

    Khi người dùng có yêu cầu về gợi ý/tư vấn sản phẩm hoặc là gợi ý mẫu/sản phẩm khác so với lần trước.
    Và bạn đã có đủ thông tin của khách hàng để tiến hành tìm sản phẩm, bạn **phải** chọn công cụ này

    QUAN TRỌNG: Để tránh trùng lặp sản phẩm đã gợi ý:
    - Sử dụng excluded_product_names: danh sách tên sản phẩm đã gợi ý trước đó
    - Hoặc sử dụng product_offset: bỏ qua N sản phẩm đầu tiên

    Args:
        description (str): mô tả về sản phẩm cần tìm kiếm. Có thể là từ khóa, tên sản phẩm, đối tượng, hoặc mô tả ngắn gọn.
            Ở dạng chuỗi, ví dụ: "áo thun nam", "quần jeans", v.v.
        price_range (list[float], optional): Khoảng giá mong muốn [min, max]. Mặc định là [0, 1e9].
        product_amount (int, optional): Số lượng sản phẩm muốn tìm (1-10). Mặc định là 5.
        product_offset (int, optional): Bỏ qua N sản phẩm đầu tiên (dùng khi cùng tiêu chí tìm kiếm)
        excluded_product_names (list[str], optional):: Danh sách tên sản phẩm cần loại trừ khỏi kết quả
    Returns:
        List[str]: Danh sách các sản phẩm phù hợp.

    Ví dụ:
        ```python
        search_advanced_tool(
            description="áo thun",
            price_range=[0, 200000],
            product_amount=3,
            product_offset=5,
        )
        ```
    """

    logging.info("find_fit_products_tool called")
    result = __searchAdvanced.search(
        description=description,
        price_range=price_range,
        product_amount=product_amount,
        product_offset=product_offset,
        excluded_product_names=excluded_product_names,
    )
    return result

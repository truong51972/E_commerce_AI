import logging
from typing import List, Optional

from dotenv import load_dotenv
from langchain.tools import tool
from pydantic import Field, validate_call

from core.services.product.search_advanced_service import SearchAdvancedService

load_dotenv()

__searchAdvanced = None


@validate_call
def init_search_advanced_service(searchAdvancedService: SearchAdvancedService):
    global __searchAdvanced
    __searchAdvanced = searchAdvancedService


@tool
@validate_call
def find_fit_products_tool(
    description: str,
    price_range: list[float] = Field(default=[0, 1e9], min_length=2, max_length=2),
    category_tier_one_name: Optional[str] = Field(
        default=None,
        description='phân loại theo đối tượng, ví dụ như "thời trang unisex", "thời trang nam", v.v.',
    ),
    category_tier_two_name: Optional[str] = Field(
        default=None,
        description='phân loại theo loại trang phục/phụ kiện chính, ví dụ như "áo", "quần", v.v.',
    ),
    category_tier_three_name: Optional[str] = Field(
        default=None,
        description='phân loại theo loại trang phục/phụ kiện cụ thể, ví dụ như "áo thun", "quần jeans", v.v.',
    ),
    k: int = Field(default=5, description="the number of output", ge=1, le=10),
) -> List[str]:
    """Tìm kiếm sản phẩm phù hợp với nhu cầu người dùng.

    Khi người dùng có yêu cầu về gợi ý/tư vấn sản phẩm.
    Và bạn đã có đủ thông tin của khách hàng để tiến hành tìm sản phẩm, bạn **phải** chọn công cụ này

    Args:
        description (str): Mô tả chi tiết nhu cầu sản phẩm (ví dụ: "áo thun cotton form rộng").
        price_range (list[float], optional): Khoảng giá mong muốn [min, max]. Mặc định là [0, 1e9].
        category_tier_one_name (Optional[str], optional): Danh mục cấp 1 (ví dụ: "thời trang nam").
        category_tier_two_name (Optional[str], optional): Danh mục cấp 2 (ví dụ: "áo").
        category_tier_three_name (Optional[str], optional): Danh mục cấp 3 (ví dụ: "áo thun").
        k (int, optional): Số lượng sản phẩm muốn tìm (1-10). Mặc định là 5.

    Returns:
        List[str]: Danh sách các sản phẩm phù hợp.

    Ví dụ:
        `find_fit_products_tool(description="áo thun", price_range=[0, 200000], category_tier_one_name="thời trang nam", category_tier_three_name="áo thun", k=3)`
    """
    logging.info("find_fit_products_tool called")
    result = __searchAdvanced.search(
        description=description,
        price_range=price_range,
        category_tier_one_name=category_tier_one_name,
        category_tier_two_name=category_tier_two_name,
        category_tier_three_name=category_tier_three_name,
        k=k,
    )
    return result

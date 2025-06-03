import logging
from typing import Optional

from langchain.tools import tool
from pydantic import Field, validate_call

from core.services.product.get_categories_service import GetCategoriesService

__get_categories = None


def init_get_categories_service(getCategoriesService: GetCategoriesService):
    global __get_categories
    __get_categories = getCategoriesService


@tool
@validate_call
def get_categories_tool(
    tier_one_category_name: Optional[str] = Field(
        default=None,
        description='phân loại theo đối tượng, ví dụ như "thời trang unisex", "thời trang nam", v.v.',
    ),
    tier_two_category_name: Optional[str] = Field(
        default=None,
        description='phân loại theo loại trang phục/phụ kiện chính, ví dụ như "áo", "quần", v.v.',
    ),
    tier_three_category_name: Optional[str] = Field(
        default=None,
        description='phân loại theo loại trang phục/phụ kiện cụ thể, ví dụ như "áo thun", "quần jeans", v.v.',
    ),
) -> list[str]:
    """
    Lấy danh sách các phân loại sản phẩm.
    Khi người dùng hỏi những câu hỏi chung chung, đã có đề cập trước đó, có liên quan đến phân loại san phẩm,
    thì **bắt buộc** sử dụng công cụ này để truy xuất

    Args:
        tier_one_category_name (Optional[str]): phân loại theo đối tượng, ví dụ như "thời trang unisex", "thời trang nam", v.v.
        tier_two_category_name (Optional[str]): phân loại theo loại trang phục/phụ kiện chính, ví dụ như "áo", "quần", v.v.
        tier_three_category_name (Optional[str]): phân loại theo loại trang phục/phụ kiện cụ thể, ví dụ như "áo thun", "quần jeans", v.v.
    Returns:
        list[str]:
            Danh sách các loại sản phẩm tương ứng với cấp độ đã chỉ định.
            Mặc định sẽ trả danh sách tất cả các loại sản phẩm cấp độ 1 (`category_tier_one`).
            Nếu chỉ định cả `tier_one_category_name` và `tier_two_category_name`, hàm sẽ trả về danh sách các loại sản phẩm cấp độ 3 (`category_tier_three`) tương ứng.
    """
    logging.info(
        "get_categories_tool called, tier_one_category_name=%s, tier_two_category_name=%s, tier_three_category_name=%s",
        tier_one_category_name,
        tier_two_category_name,
        tier_three_category_name,
    )
    return __get_categories.get_categories(
        tier_one_category_name=tier_one_category_name,
        tier_two_category_name=tier_two_category_name,
    )

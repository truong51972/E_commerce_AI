import logging
from typing import List

from dotenv import load_dotenv
from langchain.tools import tool

from core.services.product.search_advanced_service import SearchAdvancedService

load_dotenv()

searchAdvanced = SearchAdvancedService(collection_name="e_commerce_ai")


@tool
def find_fit_products_tool(
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
    logging.info("find_fit_products_tool called")
    result = searchAdvanced.search(
        text=text,
        price_range=price_range,
        categories=categories,
        k=k,
    )
    return result

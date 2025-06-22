import logging
from typing import List, Optional, Type

from dotenv import load_dotenv
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, validate_call
from src.services.product.search_advanced_service import SearchAdvancedService


class SearchAdvancedInput(BaseModel):
    """Input schema for SearchAdvancedTool"""

    description: Optional[str] = Field(
        default="",
        description="Mô tả về sản phẩm cần tìm kiếm",
    )
    price_range: List[float] = Field(
        default=[0, 1e9],
        description="Khoảng giá mong muốn [min, max]",
    )
    category_tier_one_name: Optional[str] = Field(
        default=None,
        description='Danh mục cấp 1, ví dụ: "thời trang nam"',
    )
    category_tier_two_name: Optional[str] = Field(
        default=None,
        description='Danh mục cấp 2, ví dụ: "áo"',
    )
    category_tier_three_name: Optional[str] = Field(
        default=None,
        description='Danh mục cấp 3, ví dụ: "áo thun"',
    )
    product_amount: int = Field(
        default=5,
        description="Số lượng sản phẩm muốn tìm (1-10)",
    )
    product_offset: int = Field(
        default=0,
        description="Bỏ qua N sản phẩm đầu tiên (dùng khi cùng tiêu chí tìm kiếm)",
    )
    excluded_product_names: Optional[List[str]] = Field(
        default=None,
        description="Danh sách tên sản phẩm cần loại trừ khỏi kết quả",
    )


class SearchAdvancedTool(BaseTool):
    """Tool to search for products based on advanced criteria"""

    name: str = "search_advanced_tool"
    description: str = """
    Tìm kiếm sản phẩm phù hợp với nhu cầu người dùng.

    Khi người dùng có yêu cầu về gợi ý/tư vấn sản phẩm hoặc là gợi ý mẫu/sản phẩm khác so với lần trước.
    Và bạn đã có đủ thông tin của khách hàng để tiến hành tìm sản phẩm, bạn **phải** chọn công cụ này

    QUAN TRỌNG: Để tránh trùng lặp sản phẩm đã gợi ý:
    - Sử dụng excluded_product_names: danh sách tên sản phẩm đã gợi ý trước đó
    - Hoặc sử dụng product_offset: bỏ qua N sản phẩm đầu tiên

    Args:
        description: Mô tả về sản phẩm cần tìm kiếm
        price_range: Khoảng giá mong muốn [min, max]
        category_tier_one_name: Danh mục cấp 1 (ví dụ: "thời trang nam")
        category_tier_two_name: Danh mục cấp 2 (ví dụ: "áo")
        category_tier_three_name: Danh mục cấp 3 (ví dụ: "áo thun")
        product_amount: Số lượng sản phẩm muốn tìm (1-10)
        product_offset: Bỏ qua N sản phẩm đầu tiên
        excluded_product_names: Danh sách tên sản phẩm cần loại trừ

    Returns:
        Danh sách các sản phẩm phù hợp
    """
    args_schema: Type[BaseModel] = SearchAdvancedInput

    def __init__(self, search_advanced_service: SearchAdvancedService, **kwargs):
        super().__init__(**kwargs)
        self._search_advanced_service = search_advanced_service

    def _run(
        self,
        description: Optional[str] = "",
        price_range: List[float] = [0, 1e9],
        category_tier_one_name: Optional[str] = None,
        category_tier_two_name: Optional[str] = None,
        category_tier_three_name: Optional[str] = None,
        product_amount: int = 5,
        product_offset: int = 0,
        excluded_product_names: Optional[List[str]] = None,
    ) -> List[str]:
        """Execute the search tool"""
        logging.info(
            "search_advanced_tool called with description=%s, price_range=%s, categories=[%s, %s, %s]",
            description,
            price_range,
            category_tier_one_name,
            category_tier_two_name,
            category_tier_three_name,
        )

        result = self._search_advanced_service.search(
            description=description,
            price_range=price_range,
            category_tier_one_name=(
                category_tier_one_name.lower() if category_tier_one_name else None
            ),
            category_tier_two_name=(
                category_tier_two_name.lower() if category_tier_two_name else None
            ),
            category_tier_three_name=(
                category_tier_three_name.lower() if category_tier_three_name else None
            ),
            product_amount=product_amount,
            product_offset=product_offset,
            excluded_product_names=excluded_product_names,
        )
        return result

    # async def _arun(
    #     self,
    #     description: Optional[str] = "",
    #     price_range: List[float] = [0, 1e9],
    #     category_tier_one_name: Optional[str] = None,
    #     category_tier_two_name: Optional[str] = None,
    #     category_tier_three_name: Optional[str] = None,
    #     product_amount: int = 5,
    #     product_offset: int = 0,
    #     excluded_product_names: Optional[List[str]] = None,
    # ) -> List[str]:
    #     """Execute the search tool asynchronously"""
    #     # For now, just call the sync version
    #     # You can implement async version if SearchAdvancedService supports it
    #     return self._run(
    #         description=description,
    #         price_range=price_range,
    #         category_tier_one_name=category_tier_one_name,
    #         category_tier_two_name=category_tier_two_name,
    #         category_tier_three_name=category_tier_three_name,
    #         product_amount=product_amount,
    #         product_offset=product_offset,
    #         excluded_product_names=excluded_product_names,
    #     )

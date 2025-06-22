import logging
from typing import List, Optional, Type

from dotenv import load_dotenv
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, validate_call
from src.services.product.search_advanced_service import SearchAdvancedService


class SearchBasicInput(BaseModel):
    """Input schema for SearchBasicTool"""

    description: str = Field(
        description="Mô tả về sản phẩm cần tìm kiếm. Có thể là từ khóa, tên sản phẩm, đối tượng, hoặc mô tả ngắn gọn. Ví dụ: 'áo thun nam', 'quần jeans'"
    )
    price_range: List[float] = Field(
        default=[0, 1e9], description="Khoảng giá mong muốn [min, max]"
    )
    product_amount: int = Field(
        default=1, description="Số lượng sản phẩm muốn tìm (1-10)"
    )
    product_offset: int = Field(
        default=0,
        description="Bỏ qua N sản phẩm đầu tiên (dùng khi cùng tiêu chí tìm kiếm)",
    )
    excluded_product_names: Optional[List[str]] = Field(
        default=None, description="Danh sách tên sản phẩm cần loại trừ khỏi kết quả"
    )


class SearchBasicTool(BaseTool):
    """Tool to search for products using basic criteria"""

    name: str = "search_basic_tool"
    description: str = """
    Tìm kiếm sản phẩm phù hợp với nhu cầu người dùng (phiên bản cơ bản).

    Khi người dùng có yêu cầu về gợi ý/tư vấn sản phẩm hoặc là gợi ý mẫu/sản phẩm khác so với lần trước.
    Và bạn đã có đủ thông tin của khách hàng để tiến hành tìm sản phẩm, bạn **phải** chọn công cụ này

    QUAN TRỌNG: Để tránh trùng lặp sản phẩm đã gợi ý:
    - Sử dụng excluded_product_names: danh sách tên sản phẩm đã gợi ý trước đó
    - Hoặc sử dụng product_offset: bỏ qua N sản phẩm đầu tiên

    Args:
        description: Mô tả về sản phẩm cần tìm kiếm (bắt buộc)
        price_range: Khoảng giá mong muốn [min, max]
        product_amount: Số lượng sản phẩm muốn tìm (1-10)
        product_offset: Bỏ qua N sản phẩm đầu tiên
        excluded_product_names: Danh sách tên sản phẩm cần loại trừ

    Returns:
        Danh sách các sản phẩm phù hợp

    Ví dụ:
        search_basic_tool(
            description="áo thun",
            price_range=[0, 200000],
            product_amount=3,
            product_offset=1,
        )
    """
    args_schema: Type[BaseModel] = SearchBasicInput

    def __init__(self, search_advanced_service: SearchAdvancedService, **kwargs):
        super().__init__(**kwargs)
        self._search_advanced_service = search_advanced_service

    @validate_call
    def _run(
        self,
        description: str,
        price_range: List[float] = [0, 1e9],
        product_amount: int = 1,
        product_offset: int = 0,
        excluded_product_names: Optional[List[str]] = None,
    ) -> List[str]:
        """Execute the basic search tool"""
        logging.info("search_basic_tool called with description=%s", description)

        result = self._search_advanced_service.search(
            description=description,
            price_range=price_range,
            product_amount=product_amount,
            product_offset=product_offset,
            excluded_product_names=excluded_product_names,
        )
        return result

    # async def _arun(
    #     self,
    #     description: str,
    #     price_range: List[float] = [0, 1e9],
    #     product_amount: int = 1,
    #     product_offset: int = 0,
    #     excluded_product_names: Optional[List[str]] = None,
    # ) -> List[str]:
    #     """Execute the basic search tool asynchronously"""
    #     # For now, just call the sync version
    #     # You can implement async version if SearchAdvancedService supports it
    #     return self._run(
    #         description=description,
    #         price_range=price_range,
    #         product_amount=product_amount,
    #         product_offset=product_offset,
    #         excluded_product_names=excluded_product_names,
    #     )

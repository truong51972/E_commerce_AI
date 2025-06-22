import logging
from typing import Optional, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from src.services.product.get_categories_service import GetCategoriesService


class GetCategoriesInput(BaseModel):
    """Input schema for GetCategoriesTool"""

    tier_one_category_name: Optional[str] = Field(
        default=None,
        description='phân loại theo đối tượng, ví dụ như "thời trang unisex", "thời trang nam", v.v.',
    )
    tier_two_category_name: Optional[str] = Field(
        default=None,
        description='phân loại theo loại trang phục/phụ kiện chính, ví dụ như "áo", "quần", v.v.',
    )
    tier_three_category_name: Optional[str] = Field(
        default=None,
        description='phân loại theo loại trang phục/phụ kiện cụ thể, ví dụ như "áo thun", "quần jeans", v.v.',
    )


class GetCategoriesTool(BaseTool):
    """Tool to get product categories"""

    name: str = "get_categories_tool"
    description: str = """
    Lấy danh sách các phân loại sản phẩm.
    Khi người dùng hỏi những câu hỏi chung chung, đã có đề cập trước đó, có liên quan đến phân loại sản phẩm,
    thì **bắt buộc** sử dụng công cụ này để truy xuất.
    
    Args:
        tier_one_category_name: phân loại theo đối tượng, ví dụ như "thời trang unisex", "thời trang nam"
        tier_two_category_name: phân loại theo loại trang phục/phụ kiện chính, ví dụ như "áo", "quần"
        tier_three_category_name: phân loại theo loại trang phục/phụ kiện cụ thể, ví dụ như "áo thun", "quần jeans"
    
    Returns:
        Danh sách các loại sản phẩm tương ứng với cấp độ đã chỉ định.
        Mặc định sẽ trả danh sách tất cả các loại sản phẩm cấp độ 1 (category_tier_one).
        Nếu chỉ định cả tier_one_category_name và tier_two_category_name, 
        hàm sẽ trả về danh sách các loại sản phẩm cấp độ 3 (category_tier_three) tương ứng.
    """
    args_schema: Type[BaseModel] = GetCategoriesInput

    def __init__(self, get_categories_service: GetCategoriesService, **kwargs):
        super().__init__(**kwargs)
        self._get_categories_service = get_categories_service

    def _run(
        self,
        tier_one_category_name: Optional[str] = None,
        tier_two_category_name: Optional[str] = None,
        tier_three_category_name: Optional[str] = None,
    ) -> list[str]:
        """Execute the tool"""

        logging.info(
            "get_categories_tool called, tier_one_category_name=%s, tier_two_category_name=%s, tier_three_category_name=%s",
            tier_one_category_name,
            tier_two_category_name,
            tier_three_category_name,
        )

        return self._get_categories_service.get_categories(
            tier_one_category_name=tier_one_category_name,
            tier_two_category_name=tier_two_category_name,
        )

    # async def _arun(
    #     self,
    #     tier_one_category_name: Optional[str] = None,
    #     tier_two_category_name: Optional[str] = None,
    #     tier_three_category_name: Optional[str] = None,
    # ) -> list[str]:
    #     """Execute the tool asynchronously"""
    #     # For now, just call the sync version
    #     # You can implement async version if GetCategoriesService supports it
    #     return self._run(
    #         tier_one_category_name=tier_one_category_name,
    #         tier_two_category_name=tier_two_category_name,
    #         tier_three_category_name=tier_three_category_name,
    #     )

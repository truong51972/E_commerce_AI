# src.services.product.search_advanced
import logging
from typing import List, Optional

from langchain_milvus import Milvus
from pydantic import Field, validate_call

# for validation
from src.base.service.base_embedding_service import BaseEmbeddingService
from src.base.service.base_milvus_service import BaseMilvusService


class SearchAdvancedService(BaseMilvusService, BaseEmbeddingService):
    @validate_call
    def search(
        self,
        description: Optional[str] = Field(
            default_factory=str, description="Mô tả về sản phẩm cần tìm kiếm"
        ),
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
        product_amount: int = Field(
            default=5, description="the number of output", ge=1, le=10
        ),
        product_offset: int = Field(
            default=0,
            description="Vị trí bắt đầu lấy sản phẩm (bắt đầu từ 0)",
        ),
        excluded_product_names: Optional[List[str]] = Field(
            default=None,
            description="Danh sách các tên sản phẩm cần loại trừ khỏi kết quả tìm kiếm.",
        ),
    ) -> List[str]:
        assert price_range[0] <= price_range[1], "Invalid Price Range!"

        milvus = Milvus(
            embedding_function=self._embeddings,
            collection_name=self.collection_name,
            connection_args={"uri": self.milvus_uri, "token": self.milvus_token},
        )

        expr = f"(price >= {price_range[0]} and price <= {price_range[1]}) "

        if category_tier_one_name:
            expr += f' AND category_tier_one == "{category_tier_one_name}" '

        if category_tier_two_name:
            expr += f' AND category_tier_two == "{category_tier_two_name}" '

        if category_tier_three_name:
            expr += f' AND category_tier_three == "{category_tier_three_name}" '

        if excluded_product_names:
            excluded_names_str = ", ".join(
                [f'"{name}"' for name in excluded_product_names]
            )
            expr += f" AND product_name NOT IN [{excluded_names_str}] "

        result = milvus.similarity_search(
            query=description,
            k=product_amount + product_offset,  # Lấy nhiều hơn để có thể product_offset
            expr=expr,
        )

        # Trả về kết quả từ vị trí product_offset
        return result[product_offset : product_offset + product_amount]


if __name__ == "__main__":
    # Tải biến môi trường từ file .env
    from dotenv import load_dotenv

    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(funcName)s: %(message)s",
    )

    # Khởi tạo đối tượng SearchAdvanced
    search_advanced = SearchAdvancedService(
        collection_name="e_commerce_ai",
    )

    # Thực hiện tìm kiếm
    results = search_advanced.search(
        text="áo màu xanh",
        price_range=[0, 3000000],
        category_tier_one_name="thời trang nam",
        k=5,
    )

    print(results)  # In kết quả tìm kiếm

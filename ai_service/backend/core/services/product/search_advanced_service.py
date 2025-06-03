# core.services.product.search_advanced
import logging
from typing import List, Optional


# for validation
from core.base.base_embedding import BaseEmbedding
from core.base.base_milvus import BaseMilvus
from langchain_milvus import Milvus
from pydantic import Field, validate_call


class SearchAdvancedService(BaseMilvus, BaseEmbedding):
    @validate_call
    def search(
        self,
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
        assert price_range[0] <= price_range[1], "Invalid Price Range!"

        milvus = Milvus(
            embedding_function=self._embeddings,
            collection_name=self.collection_name,
            connection_args={"uri": self.milvus_uri, "token": self.milvus_token},
        )

        # ARRAY_CONTAINS_ALL(categories, {categories})

        expr = f"(price >= {price_range[0]} and price <= {price_range[1]}) "

        if category_tier_one_name:
            expr += f' AND category_tier_one == "{category_tier_one_name}" '

        if category_tier_two_name:
            expr += f' AND category_tier_two == "{category_tier_two_name}" '

        if category_tier_three_name:
            expr += f' AND category_tier_three == "{category_tier_three_name}" '

        result = milvus.similarity_search(
            query=description,
            k=k,
            expr=expr,
        )

        return result


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

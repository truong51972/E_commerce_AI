# src.services.product.common.tools.get_categories
from typing import Optional

from pydantic import Field, model_validator, validate_call
from pymilvus import Collection

from src.base.service.base_milvus_service import BaseMilvusService


class GetCategoriesService(BaseMilvusService):

    # after init
    @model_validator(mode="after")
    def __after_init(self):
        """
        Hàm này được gọi sau khi khởi tạo đối tượng để thiết lập các thuộc tính cần thiết.
        """
        self._collection = Collection(name=self.collection_name)

        self._category_tier_map = {
            1: "category_tier_one",
            2: "category_tier_two",
            3: "category_tier_three",
        }

        return self

    @validate_call
    def get_categories(
        self,
        tier_one_category_name: Optional[str] = Field(
            default=None,
            description="Tên loại cha để lọc các loại con. Mặc định là rỗng, có thể là tên của loại cha.",
        ),
        tier_two_category_name: Optional[str] = Field(
            default=None,
            description="Tên loại con để lọc các loại con. Mặc định là rỗng, có thể là tên của loại con.",
        ),
    ) -> list[str]:
        """
        Lấy danh sách các loại sản phẩm từ cơ sở dữ liệu.
        Hữu ích khi người dùng muốn tìm kiếm các loại sản phẩm theo cấp độ phân loại.

        Các loại sản phẩm được phân cấp theo ba cấp độ, dựa trên phân loại tổng quát của sản phẩm:
        - Cấp độ 1: `category_tier_one`, ví dụ như "thời trang unisex", "đồ điện tử", v.v.
        - Cấp độ 2: `category_tier_two`, ví dụ như "áo", "quần", "điện thoại", "máy tính bảng", v.v.
        - Cấp độ 3: `category_tier_three`, ví dụ như "áo thun", "quần jeans", "iPhone", "Samsung Galaxy", v.v.

        Nếu không chỉ định `tier_one_category_name`, `tier_two_category_name`
        hàm mặc định sẽ trả về `category_tier_one`, tức là danh sách tất cả các loại sản phẩm cấp độ 1.

        Nếu người dùng chỉ định `tier_one_category_name`
            -> hàm sẽ lọc các loại con (`category_tier_two`) theo loại cha đó.
        Nếu người dùng chỉ định `tier_two_category_name`
            -> hàm sẽ lọc các loại con (`category_tier_three`) theo loại con đó.
        Nếu người dùng chỉ định cả hai `tier_one_category_name` và `tier_two_category_name`,
            -> hàm sẽ lọc các loại con (`category_tier_three`) theo loại cha và loại con đó.

        Args:
            tier_one_category_name (Optional[str]): Tên loại cha để lọc các loại con. Mặc định là rỗng.
            tier_two_category_name (Optional[str]): Tên loại con để lọc các loại con. Mặc định là rỗng.
        Returns:
            list[str]: Danh sách các loại sản phẩm tương ứng với cấp độ đã chỉ định.
        """
        expr = ""
        output_category_tier_level = 1  # default to category_tier_one

        if tier_one_category_name is not None:
            expr += f"{self._category_tier_map[1]} == '{tier_one_category_name}'"
            output_category_tier_level = 2

        if tier_two_category_name is not None:
            expr += " and " if expr else ""
            expr = f"{self._category_tier_map[2]} == '{tier_two_category_name}'"

            output_category_tier_level = 3

        return self._query_categories(
            expr=expr,
            output_field=f"{self._category_tier_map[output_category_tier_level]}",
        )

    @validate_call
    def _query_categories(
        self, expr: str, output_field: str, limit: int = 1000, offset: int = 0
    ) -> list[dict]:
        """
        query categories from the collection based on the expression and output field.
        """
        _limit = limit
        _offset = offset
        all_categories = set()  # used to store unique categories

        while True:
            # Truy vấn với limit và offset
            query_results = self._collection.query(
                expr=expr,
                output_fields=[output_field],
                limit=_limit,
                offset=_offset,
                consistency_level="Strong",  # make sure to use strong consistency
            )

            # break if no results found
            if not query_results:
                break

            for query_result in query_results:
                all_categories.add(query_result[output_field])

            _offset += _limit

        return list(all_categories)


if __name__ == "__main__":

    get_categories_tool = GetCategoriesService(collection_name="e_commerce_ai")
    categories = get_categories_tool.get_categories()
    print(categories)
    categories = get_categories_tool.get_categories(
        tier_one_category_name="thời trang nam"
    )
    print(categories)

    categories = get_categories_tool.get_categories(
        tier_one_category_name="thời trang nam",
        tier_two_category_name="giày",
    )
    print(categories)

    categories = get_categories_tool.get_categories(tier_two_category_name="áo")
    print(categories)

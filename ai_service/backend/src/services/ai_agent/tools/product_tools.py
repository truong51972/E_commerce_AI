from src.base.service.base_milvus_service import BaseMilvusService
from src.services.common.tools.get_categories_tool import GetCategoriesTool
from src.services.common.tools.search_advanced_tool import SearchAdvancedTool
from src.services.common.tools.search_basic_tool import SearchBasicTool  # noqa: F401
from src.services.product.get_categories_service import GetCategoriesService
from src.services.product.search_advanced_service import SearchAdvancedService


class ProductTools(BaseMilvusService):

    def create_tools(self):
        search_advanced_service = SearchAdvancedService(
            collection_name=self.collection_name
        )
        get_categories_service = GetCategoriesService(
            collection_name=self.collection_name
        )

        tools = [
            # SearchBasicTool(search_advanced_service=search_advanced_service),
            SearchAdvancedTool(search_advanced_service=search_advanced_service),
            GetCategoriesTool(get_categories_service=get_categories_service),
        ]
        return tools

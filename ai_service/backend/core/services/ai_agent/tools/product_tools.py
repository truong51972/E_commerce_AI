from core.base.base_milvus import BaseMilvus
from core.services.common.tools.get_categories_tool import GetCategoriesTool
from core.services.common.tools.search_advanced_tool import SearchAdvancedTool
from core.services.common.tools.search_basic_tool import SearchBasicTool
from core.services.product.get_categories_service import GetCategoriesService
from core.services.product.search_advanced_service import SearchAdvancedService


class ProductTools(BaseMilvus):

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

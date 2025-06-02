# core.services.product.search_advanced
import logging
from typing import List, Optional, Union

import langchain

# for validation
import pydantic
from core.base.base_embedding import BaseEmbedding
from core.base.base_milvus import BaseMilvus
from core.models.product.product_model import ProductModel
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_milvus import Milvus
from pydantic import BaseModel, Field, field_validator, model_validator, validate_call
from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    utility,
)


class SearchAdvancedService(BaseMilvus, BaseEmbedding):

    @validate_call
    def search(
        self,
        text: str,
        price_range: list[float] = [0, 1e9],
        categories: list[str] = ["category_1", "category_2"],
        k: int = 5,
    ) -> List[str]:
        assert price_range[0] <= price_range[1], f"Invalid Price Range!"

        milvus = Milvus(
            embedding_function=self._embeddings,
            collection_name=self.collection_name,
            connection_args={"uri": self.milvus_uri, "token": self.milvus_token},
        )

        # ARRAY_CONTAINS_ALL(categories, {categories})

        expr = f"""
                    (price >= {price_range[0]} and price <= {price_range[1]})
                    OR
                    ARRAY_CONTAINS_ANY(categories, {categories})
                """

        result = milvus.similarity_search(
            query=text,
            k=k,
            expr=expr,
        )

        # result = [
        #     {"id": doc.metadata["id"], "product_name": doc.metadata["product_name"]}
        #     for doc in result
        # ]

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
        text="áo", price_range=[0, 3000000], categories=["áo"], k=5
    )

    print(results)  # In kết quả tìm kiếm

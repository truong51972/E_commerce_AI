from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_milvus import Milvus
from pydantic import BaseModel, field_validator, Field, model_validator
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
import logging

import langchain
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from utils.models.products import ProductsActions

class QuickSearch(ProductsActions):
    def search(
        self,
        text,
        price_range: list[float] = [0, 1e9],
        categories: list[str] = ["category_1", "category_2"],
        k: int = 5,
    ):
        assert price_range[0] <= price_range[1], f"Invalid Price Range!"

        milvus = Milvus(
            embedding_function=self._embeddings,
            collection_name=self.collection_name,
            connection_args={"uri": self.milvus_uri, "token": self.milvus_token},
        )

        expr = f"""
                    (price >= {price_range[0]} and price <= {price_range[1]})
                    AND
                    ARRAY_CONTAINS_ALL(categories, {categories})
                """

        result = milvus.similarity_search(
            query=text,
            k=k,
            expr=expr,
        )

        result = [
            {"id": doc.metadata["id"], "product_name": doc.metadata["product_name"]}
            for doc in result
        ]

        return result
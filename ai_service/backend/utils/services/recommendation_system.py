from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_milvus import Milvus
from pydantic import BaseModel, field_validator, Field, model_validator
from pymilvus import MilvusClient, connections, FieldSchema, CollectionSchema, DataType, Collection, utility
import logging

import langchain
from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from utils.models.products import ProductsActions
import json


class RecommendationSystem(ProductsActions):

    def search(self, ids: list[int]):
        collection = Collection(name=self.collection_name)

        result = collection.query(expr=f"id IN {ids}", output_fields=["id", "vector"])

        print(len(result[0]["vector"]))

        search_params = {
            "metric_type": "COSINE",
            "params": {"ef": 10},
        }

        res = collection.search(
            data=[result[0]["vector"]],
            anns_field="vector",
            param=search_params,
            limit=3,
            output_fields=["id"],
            expr=f"id NOT IN {ids}"
        )

        for hits in res:
            print("TopK results:")
            for hit in hits:
                print(hit)


if __name__ == "__main__":
    import pandas as pd
    from dotenv import load_dotenv
    load_dotenv()

    # langchain.debug = True

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(funcName)s: %(message)s")

    rs = RecommendationSystem()

    rs.search(ids=[0, 1, 2, 3])
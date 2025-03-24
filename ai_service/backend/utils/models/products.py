import uuid
import hashlib

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

from pathlib import Path

from utils.base.milvus_base import MilvusBase


class ProductsActions(MilvusBase):

    @model_validator(mode="after")
    def __after_init(self):
        return self

    def create_collection(self):
        assert not self.is_collection_exists(), f"'{self.collection_name}' exists!"

        embedding_dim = len(self._embeddings.embed_documents([""])[0])

        fields = [
            FieldSchema(
                name="id", dtype=DataType.INT64, is_primary=True, auto_id=False
            ),
            FieldSchema(name="product_name", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="price", dtype=DataType.DOUBLE),
            FieldSchema(name="description", dtype=DataType.VARCHAR, max_length=16384),
            FieldSchema(
                name="categories",
                dtype=DataType.ARRAY,
                element_type=DataType.VARCHAR,
                max_length=2048,
                max_capacity=50,
            ),
            FieldSchema(name="product_link", dtype=DataType.VARCHAR, max_length=2048),
            FieldSchema(
                name="vector", dtype=DataType.FLOAT_VECTOR, dim=embedding_dim
            ),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=16384),
        ]
        schema = CollectionSchema(fields, description="Product collection with scalar fields")
        collection = Collection(name=self.collection_name, schema=schema)

        index_params = {
            "metric_type": "COSINE",
            "index_type": "HNSW",
            "params": {"M": 8, "efConstruction": 64}
        }
        collection.create_index(field_name="vector", index_params=index_params)

        collection.load()

    def add_or_edit_records(self, data: list[dict[str:str]] | dict[str:str]):
        def md5_to_int64(data: str) -> int:
            hash_bytes = hashlib.md5(data.encode()).digest()
            int_64bit = int.from_bytes(hash_bytes[:8], 'big', signed=True)  # Dạng signed
            return int_64bit
        
        if not isinstance(data, list): data = [data]

        collection = Collection(name=self.collection_name)

        texts = []
        logging.info("Loading data...")
        for record in data:
            record["price"] = record["price"][:-1]
            text = "\n".join([
                f"Product Name: {record['product_name']}",
                f"Price: {record['price']}",
                f"Categories: {record['categories']}",
                f"Description: {record['description']}",
            ])

            record['id'] = record.get('id', md5_to_int64(text))

            texts.append(text)

            if isinstance(record["categories"], str):
                record["categories"] = record["categories"].split(', ')

            if isinstance(record["price"], str):
                record["price"] = float(record["price"].replace(",",""))

        logging.info("Embedding...")
        vectors = self._embeddings.embed_documents(texts)

        for i in range(len(data)):
            texts[i] += f"\nProduct Link: {data[i]['product_link']}"

            data[i]["vector"] = vectors[i]
            data[i]["text"] = texts[i]

        logging.info("Loading data into database...")
        collection.insert(data)
        collection.load()
        logging.info("Done!")

    def get_record(self, id):
        output_fields = [
            "id",
            "product_name",
            "description",
            "price",
            "categories",
            "product_link",
        ]
        self.read_record(id=id, output_fields=output_fields)

    def add_new_record(self, data):
        assert self.is_collection_exists(), f"'{self.collection_name}' does not exist!"
        assert not self.is_id_exists(data['id']), f"id= {data['id']} already exists!"

        self.add_or_edit_records(data)

    def edit_record(self, data):
        assert self.is_collection_exists(), f"'{self.collection_name}' does not exist!"
        assert self.is_id_exists(data['id']), f"id={data['id']} does not exist!"

        self.add_or_edit_records(data)


if __name__ == "__main__":
    import pandas as pd
    from dotenv import load_dotenv
    load_dotenv()

    # langchain.debug = True

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(funcName)s: %(message)s")

    products_actions = ProductsActions(collection_name="test_08")

    # df = pd.read_excel("./utils/.data/kenta_pant.xlsx")
    df = pd.read_excel("./utils/.data/MLB.xlsx")
    
    data = df.to_dict(orient="records")

    products_actions.add_or_edit_records(data)
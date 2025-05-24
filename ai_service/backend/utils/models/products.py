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

def create_unique_id(text: str) -> int:
    '''Create a unique id with text as a seed'''
    assert isinstance(text, str), "text must be a string"
    assert len(text) > 0, "text must not be empty"
    # assert len(text) < 1000, "text must not be too long"

    # create a unique id for the product
    hash_bytes = hashlib.md5(text.encode()).digest()
    int_64bit = int.from_bytes(hash_bytes[:8], 'big', signed=True)  # Dạng signed
    return int_64bit

class Products(BaseModel):
    '''Product model'''
    id: int | None = Field(default=None)
    product_name: str
    price: float
    description: str
    categories: list[str]
    product_link: str
    vector: list[float] = Field(default_factory=list)
    text: str = Field(default_factory=str) # text for context
    text_for_embedding: str = Field(default_factory=str, exclude=True) # text for embedding, exclude from model while converting to dict

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "product_name": "Product Name",
                "price": 100.0,
                "description": "Product Description",
                "categories": ["Category1", "Category2"],
                "product_link": "https://example.com/product/1",
            }
        }

    # check price, if not float, try to convert to float
    @field_validator("price", mode="before")
    def check_price(cls, v):
        if isinstance(v, str):
            try:
                v = float(v.replace(",", ""))
            except ValueError:
                raise ValueError("Price must be a float or a string that can be converted to a float")
        return v

    # check categories, if not list, try to convert to list
    @field_validator("categories", mode="before")
    def check_categories(cls, v):
        if isinstance(v, str):
            v = v.split(", ")
        elif not isinstance(v, list):
            raise ValueError("Categories must be a list or a string that can be converted to a list")
        return v
    
    # after init, create a new text for embedding
    @model_validator(mode="after")
    def create_text_for_embedding(self):
        # create a new text for embedding
        self.text_for_embedding = "\n".join([
            f"Product Name: {self.product_name}",
            f"Price: {self.price}",
            f"Categories: {self.categories}",
            f"Description: {self.description}",
        ])
        return self

    # after init, create a new text for context
    @model_validator(mode="after")
    def create_text(self):
        # create a new text for context
        self.text = "\n".join([
            f"Product Name: {self.product_name}",
            f"Price: {self.price}",
            f"Categories: {self.categories}",
            f"Description: {self.description}",
            f"Product Link: {self.product_link}",
        ])
        return self

    # after init, if id not exists, create a new id from defined seed
    @model_validator(mode="after")
    def check_id(self):
        if self.id is None:
            # create a new id from defined seed
            seed = self.description + self.product_name + self.product_link
            if seed:
                self.id = create_unique_id(seed)
            else:
                raise ValueError("ID must be provided or text must be provided to create a new ID")
        return self

class ProductsActions(MilvusBase):

    @model_validator(mode="after")
    def __after_init(self):
        return self

    def create_collection(self):
        '''Create collection in Milvus'''
        # Check if collection exists
        assert not self.is_collection_exists(), f"'{self.collection_name}' exists!"

        # get embedding dimension
        embedding_dim = len(self._embeddings.embed_documents([""])[0])

        # Create collection schema
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

        # create collection with schema
        schema = CollectionSchema(fields, description="Product collection with scalar fields")
        collection = Collection(name=self.collection_name, schema=schema)

        # Create index for searching 
        index_params = {
            "metric_type": "COSINE",
            "index_type": "HNSW",
            "params": {"M": 8, "efConstruction": 64}
        }
        collection.create_index(field_name="vector", index_params=index_params)

        collection.load()

    def add_or_edit_records(self, data: list[dict[str:str]] | dict[str:str]):
        '''Add or edit records in Milvus'''
        assert self.is_collection_exists(), f"'{self.collection_name}' does not exist!"
        assert isinstance(data, (list, dict)), "data must be a list or a dict"
        assert all(isinstance(record, dict) for record in data), "data must be a list of dicts"

        # convert to list if data is a dict
        if not isinstance(data, list): data = [data]    

        # Check if collection exists
        assert self.is_collection_exists(), f"'{self.collection_name}' does not exist!"
        collection = Collection(name=self.collection_name)

        validated_records = []

        texts = []
        logging.info("Loading data...")
        for record in data:
            validated_record = Products(**record)
            validated_records.append(validated_record)

            texts.append(validated_record.text_for_embedding)

        # embed text
        logging.info("Embedding...")
        vectors = self._embeddings.embed_documents(texts)

        # add vectors to validated records
        for i in range(len(validated_records)):
            validated_records[i].vector = vectors[i]

        logging.info("Loading data into database...")
        collection.insert([record.model_dump() for record in validated_records])
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
        return self.read_record(id=id, output_fields=output_fields)

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

    products_actions = ProductsActions(collection_name="e_commerce_ai")

    df = pd.read_excel("./utils/.data/MLB.xlsx")
    # df = pd.read_excel("utils/.data/kenta_ao_khoac.xlsx")
    # df = pd.read_excel("utils/.data/kenta_quan_short.xlsx")
    # df = pd.read_excel("utils/.data/kenta_quan.xlsx")
    # df = pd.read_excel("utils/.data/Dataman.xlsx")
    # df = pd.read_excel("utils/.data/5fasion_200.xlsx")
    
    data = df.to_dict(orient="records")

    products_actions.add_or_edit_records(data)
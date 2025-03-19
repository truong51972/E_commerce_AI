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
from abc import ABC, abstractmethod


class MilvusBase(ABC, BaseModel):
    milvus_uri: str = Field(default="http://localhost:19530",min_length=10,max_length=100,)
    milvus_token: str = Field(default="root:Milvus", min_length=5, max_length=100)
    collection_name: str = Field(default="default_collection_name", min_length=1, max_length=100)

    embedding_model: str = Field(default="models/text-embedding-004", min_length=5, max_length=100)
    llm_model: str = Field(default="gemini-2.0-flash", min_length=5, max_length=100)

    auto_create_collection: bool = Field(default=True)

    @model_validator(mode="after")
    def __after_init(self):
        self.connect_milvus()

        self._embeddings = GoogleGenerativeAIEmbeddings(model=self.embedding_model)
        self._llm = ChatGoogleGenerativeAI(model=self.llm_model)

        if not self.is_collection_exists() and self.auto_create_collection:
            logging.info(f"Creating new collection...")
            self.create_collection()

        return self
    
    def connect_milvus(self):
        if not connections.has_connection('default'):
            logging.info("Connecting to Milvus database...")
            connections.connect(uri=self.milvus_uri, token=self.milvus_token)

    @abstractmethod
    def create_collection(self):
        pass

    def is_collection_exists(self):
        return utility.has_collection(self.collection_name)

    def is_id_exists(self, id):
        collection = Collection(name=self.collection_name)
        result = collection.query(f"id == {id}")
        return True if result else False
    
    def create_record(self, data):
        assert self.is_collection_exists(), f"'{self.collection_name}' does not exist!"
        assert not self.is_id_exists(data['id']), f"id= {data['id']} already exists!"

        self._add_or_edit_record(data)

    def read_record(self, id, output_fields=["id"]):
        assert self.is_collection_exists(), f"'{self.collection_name}' does not exist!"
        assert self.is_id_exists(id), f"id= {id} does not exist!"

        collection = Collection(name=self.collection_name)

        result = collection.query(
            f"id == {id}",
            output_fields=output_fields
        )[0]

        result['collection_name'] = self.collection_name

        return result

    def update_record(self, data):
        assert self.is_collection_exists(), f"'{self.collection_name}' does not exist!"
        assert self.is_id_exists(data['id']), f"id={data['id']} does not exist!"

        self._add_or_edit_record(data)

    def delete_record(self, id):
        assert self.is_id_exists(id), f"id= {id} does not exist!"
        collection = Collection(name=self.collection_name)

        collection.delete(expr=f"id == {id}")
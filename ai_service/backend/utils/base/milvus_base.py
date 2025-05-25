from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_milvus import Milvus
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

# for validation
import pydantic
from pydantic import BaseModel, field_validator, Field, model_validator, validate_call
from typing import List, Optional, Union

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
        self._llm = ChatGoogleGenerativeAI(model=self.llm_model, temperature=0.2)

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

    @validate_call
    def is_id_exists(self, id:int) -> bool:
        collection = Collection(name=self.collection_name)
        result = collection.query(f"id == {id}")
        return True if result else False
    
    # def create_record(self, data):
    #     assert self.is_collection_exists(), f"'{self.collection_name}' does not exist!"
    #     assert not self.is_id_exists(data['id']), f"id= {data['id']} already exists!"

    #     self._add_or_edit_record(data)

    @validate_call
    def read_record(self, id : int, output_fields : List[str] = ["id"]):
        assert self.is_collection_exists(), f"'{self.collection_name}' does not exist!"
        assert self.is_id_exists(id), f"id= {id} does not exist!"

        collection = Collection(name=self.collection_name)

        result = collection.query(
            f"id == {id}",
            output_fields=output_fields
        )[0]

        result['collection_name'] = self.collection_name

        return result

    # def update_record(self, data):
    #     assert self.is_collection_exists(), f"'{self.collection_name}' does not exist!"
    #     assert self.is_id_exists(data['id']), f"id={data['id']} does not exist!"

    #     self._add_or_edit_record(data)

    def delete_record(self, id : int) -> int:
        """delete_record by id

        Args:
            id (int): record id to delete

        Returns:
            int: total number of deleted records
        """
        if not self.is_id_exists(id): raise ValueError(f"id= {id} does not exist!")
        collection = Collection(name=self.collection_name)

        return collection.delete(expr=f"id == {id}")
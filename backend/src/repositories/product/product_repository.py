# src.repositories.product.product_repository
import logging
from typing import List

import langchain

# for validation
from pydantic import model_validator, validate_call
from pymilvus import (
    Collection,
    CollectionSchema,
)

from src.base.service.base_embedding_service import BaseEmbeddingService
from src.base.service.base_llm_service import BaseLlmService
from src.base.service.base_milvus_service import BaseMilvusService
from src.common.generate_milvus_field_schemas_from_pydantic import (
    generate_milvus_field_schemas_from_pydantic,
)
from src.models.product.product_model import ProductModel


class ProductRepository(BaseLlmService, BaseEmbeddingService, BaseMilvusService):

    @model_validator(mode="after")
    def __after_init(self):

        if not self.is_collection_exists():
            logging.info(
                f"Collection '{self.collection_name}' does not exist. Creating a new collection..."
            )

            fields = generate_milvus_field_schemas_from_pydantic(
                pydantic_model=ProductModel, embedding_dim=self.embedding_dim
            )

            # create collection with schema
            schema = CollectionSchema(
                fields, description="Product collection with scalar fields"
            )
            self._collection = Collection(name=self.collection_name, schema=schema)

            # Create index for searching
            index_params = {
                "metric_type": "COSINE",
                "index_type": "HNSW",
                "params": {"M": 8, "efConstruction": 64},
            }
            self._collection.create_index(
                field_name="vector", index_params=index_params
            )

            self._collection.load()

        else:
            logging.info(f"Using '{self.collection_name}' collection.")
            self._collection = Collection(name=self.collection_name)

        return self

    @validate_call
    def embed_data(self, data: List[ProductModel]) -> List[ProductModel]:
        """Embed data using the configured embeddings model."""
        texts = [item.text_for_embedding for item in data]
        vectors = self._embeddings.embed_documents(texts)

        # insert vectors into the data
        for i, item in enumerate(data):
            item.vector = vectors[i]

        return data

    @validate_call
    def is_ids_exists(self, ids: List[int]) -> bool:
        """Check if all ids exist in the collection"""
        results = self._collection.query(f"id in {ids}")
        return len(results) > 0

    @validate_call
    def create_records(self, data: List[ProductModel]):
        """Add records to the collection."""

        if self.is_ids_exists([item.id for item in data]):
            raise ValueError("Contains existing ids.")

        # Embed data
        data = self.embed_data(data)

        # Insert records into the collection
        self._collection.insert([item.model_dump() for item in data])
        self._collection.load()
        logging.info("Records added successfully.")

    @validate_call
    def update_records(self, data: List[ProductModel]):
        """Edit existing records in the collection."""

        if not self.is_ids_exists(
            [item.id for item in data if item.get("id", None) is not None]
        ):
            raise ValueError("Contains non-existing ids.")

        # Embed data
        data = self.embed_data(data)

        # Insert records into the collection
        self._collection.insert([item.model_dump() for item in data])
        self._collection.load()
        logging.info("Records edited successfully.")

    @validate_call
    def read_records(self, ids: List[int]) -> List[ProductModel]:
        """Get records by ids."""

        if not self.is_ids_exists(ids):
            raise ValueError("Contains non-existing ids.")

        results = self._collection.query(
            expr=f"id IN {ids}",
            output_fields=[
                field.name
                for field in self._collection.schema.fields
                if field.name not in ["vector"]  # Exclude vector field
            ],
        )
        return results

    @validate_call
    def delete_records(self, id: List[int]) -> int:
        """delete_record by id

        Args:
            id (int): record id to delete

        Returns:
            int: total number of deleted records
        """
        return self._collection.delete(expr=f"id IN {id}")


if __name__ == "__main__":
    import pandas as pd
    from dotenv import load_dotenv

    load_dotenv()

    langchain.debug = True

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s:[%(levelname)-4s] [%(module)s] [%(funcName)s]: %(message)s",
    )

    products_actions = ProductRepository(collection_name="e_commerce_ai")

    # df = pd.read_excel("src/.data/MLB.xlsx")
    # df = pd.read_excel("src/.data/kenta_ao_khoac.xlsx")
    # df = pd.read_excel("utils/.data/kenta_quan_short.xlsx")
    # df = pd.read_excel("utils/.data/kenta_quan.xlsx")
    # df = pd.read_excel("utils/.data/Dataman.xlsx")
    # df = pd.read_excel("utils/.data/5fasion_200.xlsx")
    df = pd.read_excel("src/.data/full_data.xlsx")
    df.columns = df.columns.str.lower()

    data = df.to_dict(orient="records")

    products_actions.create_records(data)

    # got_records = products_actions.read_records([-9188129299376391335, -6305067348861834881])
    # for record in got_records:
    #     print(record)
    #     print()

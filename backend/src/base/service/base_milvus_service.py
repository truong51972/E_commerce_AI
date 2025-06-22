# src.base.service.base_milvus
import logging

# for validation
from pydantic import BaseModel, Field, model_validator
from pymilvus import connections, utility


class BaseMilvusService(BaseModel):
    milvus_uri: str = Field(
        default="http://localhost:19530",
        min_length=10,
        max_length=100,
    )
    milvus_token: str = Field(default="root:Milvus", min_length=5, max_length=100)
    collection_name: str = Field(
        default="default_collection_name", min_length=1, max_length=100
    )

    auto_create_collection: bool = Field(default=True)

    @model_validator(mode="after")
    def __after_init(self):
        if not connections.has_connection("default"):
            logging.info("Connecting to Milvus database...")
            connections.connect(uri=self.milvus_uri, token=self.milvus_token)

        return self

    def is_collection_exists(self):
        return utility.has_collection(self.collection_name)

    # def create_record(self, data):
    #     assert self.is_collection_exists(), f"'{self.collection_name}' does not exist!"
    #     assert not self.is_id_exists(data['id']), f"id= {data['id']} already exists!"

    #     self._add_or_edit_record(data)


if __name__ == "__main__":
    # Example usage
    milvus = BaseMilvusService()

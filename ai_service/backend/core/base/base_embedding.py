import logging
from typing import List, Optional, Union

# for validation
import pydantic
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from pydantic import BaseModel, Field, field_validator, model_validator, validate_call


class BaseEmbedding(BaseModel):
    embedding_model: str = Field(
        default="models/text-embedding-004", min_length=5, max_length=100
    )

    embedding_dim: Optional[int] = Field(
        default=None,
        ge=1,
        description="The dimension of the embeddings, set after initialization if get_embedding_dim is True.",
    )

    @model_validator(mode="after")
    def __after_init(self):
        self._embeddings = GoogleGenerativeAIEmbeddings(model=self.embedding_model)

        if self.embedding_dim is None:
            self.embedding_dim = len(self._embeddings.embed_documents([""])[0])
            logging.info(f"Embedding dimension: {self.embedding_dim}")

        return self

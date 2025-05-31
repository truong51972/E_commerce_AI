import logging
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

# for validation
import pydantic
from pydantic import BaseModel, field_validator, Field, model_validator, validate_call
from typing import List, Optional, Union

class BaseEmbedding(BaseModel):
    embedding_model: str = Field(default="models/text-embedding-004", min_length=5, max_length=100)

    @model_validator(mode="after")
    def __after_init(self):
        self._embeddings = GoogleGenerativeAIEmbeddings(model=self.embedding_model)
        self._embedding_dim = len(self._embeddings.embed_documents([""])[0])

        logging.info(f"Embedding dimension: {self._embedding_dim}")

        return self
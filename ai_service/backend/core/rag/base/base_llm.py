from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_milvus import Milvus
import logging

# for validation
import pydantic
from pydantic import BaseModel, field_validator, Field, model_validator, validate_call
from typing import List, Optional, Union

class BaseLLM(BaseModel):
    embedding_model: str = Field(default="models/text-embedding-004", min_length=5, max_length=100)
    llm_model: str = Field(default="gemini-2.0-flash", min_length=5, max_length=100)

    @model_validator(mode="after")
    def __after_init(self):
        self._embeddings = GoogleGenerativeAIEmbeddings(model=self.embedding_model)
        self._llm = ChatGoogleGenerativeAI(model=self.llm_model, temperature=0.2)

        # get embedding dimension
        self._embedding_dim = len(self._embeddings.embed_documents([""])[0])

        logging.info(f"Embedding dimension: {self._embedding_dim}")

        return self

if __name__ == "__main__":
    # Example usage
    base_milvus = BaseLLM()

    print(f"Embedding Model: {base_milvus.embedding_model}")
    print(f"LLM Model: {base_milvus.llm_model}")
    print(f"Embedding Dimension: {base_milvus._embedding_dim}")
    print("BaseMilvus initialized successfully.")
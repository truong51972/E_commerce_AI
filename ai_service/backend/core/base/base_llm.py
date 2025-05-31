from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_milvus import Milvus
import logging

# for validation
import pydantic
from pydantic import BaseModel, field_validator, Field, model_validator, validate_call
from typing import List, Optional, Union

class BaseLLM(BaseModel):
    llm_model: str = Field(default="gemini-2.0-flash", min_length=5, max_length=100)

    @model_validator(mode="after")
    def __after_init(self):
        self._llm = ChatGoogleGenerativeAI(model=self.llm_model, temperature=0.2)
        return self
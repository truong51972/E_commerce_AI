from typing import Optional

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
)

# for validation
from pydantic import BaseModel, Field, model_validator


class BaseLlmService(BaseModel):
    llm_model: str = Field(default="gemini-2.0-flash", min_length=5, max_length=100)

    llm_temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Temperature for the LLM, controls randomness in responses.",
    )
    llm_top_p: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Top-p sampling for the LLM, controls diversity in responses.",
    )
    llm_top_k: Optional[int] = Field(
        default=None,
        ge=1,
        le=1000,
        description="Top-k sampling for the LLM, controls the number of highest probability tokens to consider.",
    )

    @model_validator(mode="after")
    def __after_init(self):
        self._llm = ChatGoogleGenerativeAI(
            model=self.llm_model,
            temperature=self.llm_temperature,
            top_p=self.llm_top_p,
            top_k=self.llm_top_k,
        )
        return self

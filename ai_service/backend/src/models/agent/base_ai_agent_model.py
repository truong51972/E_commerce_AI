# for validation
import uuid
from typing import Optional

# for validation
from pydantic import BaseModel, Field, model_validator


class BaseAgentMessModel(BaseModel):
    """
    Represents the state of an AI agent, including its name, description, and current status.
    """

    session_id: Optional[str] = Field(
        default="00000000-0000-0000-0000-000000000000",
        description="Unique identifier for the session",
    )

    user_id: Optional[str] = Field(
        default="0",
        description="Unique identifier for the user",
    )

    user_input: str = Field(
        default="",
        description="Input from the user",
    )

    messages: str = Field(
        default="Message to be processed by the AI agent",
        description="Message to be processed by the AI agent",
    )

    @model_validator(mode="after")
    def create_session_id(self):
        """create a session id if not provided"""
        if self.session_id is None:
            self.session_id = str(uuid.uuid4())
        return self

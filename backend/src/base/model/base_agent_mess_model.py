import uuid
from typing import Optional

# for validation
from pydantic import (
    BaseModel,
    Field,
    model_validator,
)


class BaseAgentMessModel(BaseModel):
    """
    Represents the state of an AI agent, including its name, description, and current status.
    """

    session_id: Optional[str] = Field(
        default=None,
        description="Unique identifier for the session",
        examples=["00000000-0000-0000-0000-000000000000"],
    )

    user_id: str = Field(
        description="Unique identifier for the user",
        examples=["0"],
    )

    messages: str = Field(
        description="Message to be processed by the AI agent",
        examples=["Message to be processed by the AI agent"],
    )

    @model_validator(mode="after")
    def create_session_id(self):
        """create a session id if not provided"""
        if self.session_id is None:
            self.session_id = str(uuid.uuid4())
        return self

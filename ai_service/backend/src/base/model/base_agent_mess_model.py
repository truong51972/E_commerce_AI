# for validation
import uuid
from typing import Optional

# for validation
from pydantic import (
    BaseModel,
    model_validator,
)


class BaseAgentMessModel(BaseModel):
    """
    Represents the state of an AI agent, including its name, description, and current status.
    """

    session_id: Optional[str] = (
        "00000000-0000-0000-0000-000000000000"  # Unique identifier for the session
    )
    user_id: Optional[str] = "0"  # Unique identifier for the user
    messages: str = (
        "Message to be processed by the AI agent"  # Message to be processed by the AI agent
    )

    @model_validator(mode="after")
    def create_session_id(self):
        """create a session id if not provided"""
        if self.session_id is None:
            self.session_id = str(uuid.uuid4())
        return self

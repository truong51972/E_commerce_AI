# for validation
from typing import Optional

# for validation
from pydantic import Field

from src.base.model.base_agent_mess_model import BaseAgentMessModel


class AgentStateForDbModel(BaseAgentMessModel):
    """
    Represents the state of an AI agent, including its name, description, and current status.
    """

    intent: Optional[str] = Field(
        default="greeting",  # Default intent if not specified
        description="Intent of the AI agent, e.g., 'greeting', 'search', etc.",
    )

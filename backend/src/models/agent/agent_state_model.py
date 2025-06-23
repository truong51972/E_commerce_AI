from typing import Annotated, List, Optional

from langgraph.graph.message import add_messages
from pydantic import Field

from src.base.model.base_agent_mess_model import BaseAgentMessModel

# for validation


class AgentStateModel(BaseAgentMessModel):
    """
    Represents the state of an AI agent, including its name, description, and current status.
    """

    session_id: str = Field(
        default_factory=str,
        description="Unique identifier for the session",
    )

    user_id: str = Field(
        default_factory=str,
        description="Unique identifier for the user",
    )

    user_input: str = Field(
        default="user input",
        description="Input from the user",
    )
    intent: Optional[str] = Field(
        default="greeting",  # Default intent if not specified
        description="Intent of the AI agent, e.g., 'greeting', 'search', etc.",
    )
    messages: Annotated[List, add_messages] = []  # Messages in string format

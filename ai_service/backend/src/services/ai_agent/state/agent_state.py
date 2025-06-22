from typing import Annotated, List

from langgraph.graph.message import add_messages
from pydantic import BaseModel


class AgentState(BaseModel):
    """
    Represents the state of an AI agent, including its name, description, and current status.
    """

    user_input: str  # Input from the user
    intent: str = "greeting"  # Default intent if not specified
    messages: Annotated[List, add_messages] = []  # Messages in string format

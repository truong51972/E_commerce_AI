from sqlmodel import Field, SQLModel

from src.base.model.base_agent_mess_model import BaseAgentMessModel


class ConversationRepository(BaseAgentMessModel, SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)

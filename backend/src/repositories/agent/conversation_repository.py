# src.repositories.agent.conversation_repository
import json

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
)
from langchain_core.messages.tool import ToolMessage
from sqlmodel import Field, Session, SQLModel, select

from src import engine
from src.models.agent.agent_state_for_db_model import AgentStateForDbModel
from src.models.agent.agent_state_model import AgentStateModel


class ConversationRepository(AgentStateForDbModel, SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)


def load_conversations(session_id: str, user_id: str) -> AgentStateModel | None:
    """
    Retrieve a conversation by session ID and user ID.
    """
    all_records = None
    with Session(engine) as session:
        all_records = session.exec(
            select(ConversationRepository).where(
                ConversationRepository.session_id == session_id,
                ConversationRepository.user_id == user_id,
            )
        ).all()

    messages = []
    last_intent = None

    if len(all_records) == 0:
        return None

    for record in all_records:
        parsed_messages = json.loads(record.messages)
        message_type = parsed_messages.get("type", "unknown")
        if message_type == "human":
            message = HumanMessage(**parsed_messages)
        elif message_type == "ai":
            message = AIMessage(**parsed_messages)
        elif message_type == "tool":
            message = ToolMessage(**parsed_messages)

        messages.append(message)
        last_intent = record.intent

    return AgentStateModel(
        session_id=session_id,
        user_id=user_id,
        messages=messages,
        intent=last_intent,
    )


def save_conversation(
    agent_state: AgentStateModel,
    number_of_last_messages: int = 1,
) -> None:
    """
    Save a conversation in the agent state.
    """

    # Save to database
    with Session(engine) as session:
        for message in agent_state.messages[-number_of_last_messages:]:
            if isinstance(message, BaseMessage):
                message_dict = message.model_dump()
                message_dict["type"] = message.type
            else:
                message_dict = {"content": str(message), "type": "unknown"}

            agent_state_for_db = AgentStateForDbModel(
                session_id=agent_state.session_id,
                user_id=agent_state.user_id,
                messages=json.dumps(message_dict, ensure_ascii=False),
                intent=agent_state.intent,
            )

            conversation_record = ConversationRepository.model_validate(
                agent_state_for_db
            )
            session.add(conversation_record)

        session.commit()


if __name__ == "__main__":
    session_id = "00000000-0000-0000-0000-000000000000"
    user_id = "0"

    conversation = load_conversations(session_id, user_id)
    # print(conversation)

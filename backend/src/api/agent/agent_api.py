from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from sqlmodel import Session, SQLModel, select

from src import engine, logger
from src.base.model.base_agent_mess_model import BaseAgentMessModel
from src.cache import redis_client
from src.models.agent.agent_state_model import AgentStateModel
from src.repositories.agent.conversation_repository import (
    ConversationRepository,  # noqa: F401  # noqa: F401
)
from src.services.ai_agent.agent import AIAgent

# Load database configuration from environment variables (Docker Compose)

ai_agent = None  # Global variable to hold the AI agent instance


@asynccontextmanager
async def lifespan(app: FastAPI):
    global ai_agent

    SQLModel.metadata.create_all(engine)
    ai_agent = AIAgent(
        collection_name="e_commerce_ai",
        llm_temperature=0.1,
    )
    yield


router = APIRouter(lifespan=lifespan)


@router.post("/ai_agent")
def ai_agent_api(request: BaseAgentMessModel) -> BaseAgentMessModel:
    """
    Endpoint to handle AI agent requests.
    """
    # Load conversation from cache
    cache_key = f"conversation_{request.user_id}:{request.session_id}"
    cached_agent_state = redis_client.get(cache_key)

    if cached_agent_state:  # Cache hit
        # Deserialize cached state
        logger.info(
            f"Cache hit for conversation_{request.user_id}:{request.session_id}"
        )
        agent_state = AgentStateModel.model_validate_json(cached_agent_state)
        agent_state.user_input = request.messages

    else:  # Cache miss
        with Session(engine) as session:
            query_data = session.exec(
                select(ConversationRepository).where(
                    ConversationRepository.session_id == request.session_id,
                    ConversationRepository.user_id == request.user_id,
                )
            )

            # if len(query_data.all()) == 0:
            # If no data found, create a new agent state
            agent_state = AgentStateModel(
                session_id=request.session_id, user_input=request.messages
            )

            print(f"Result: {query_data.all()}")

    # Process with AI agent
    processed_state = AgentStateModel.model_validate(ai_agent.invoke(agent_state))

    # Save updated state to cache
    redis_client.setex(cache_key, 600, processed_state.model_dump_json())

    # Prepare response
    response = BaseAgentMessModel(
        user_id=processed_state.user_id,
        session_id=processed_state.session_id,
        messages=(
            processed_state.messages[-1].model_dump_json()
            if processed_state.messages
            else ""
        ),
    )

    # Save to database
    conversation_record = ConversationRepository.model_validate(response)
    with Session(engine) as session:
        session.add(conversation_record)
        session.commit()

    return response

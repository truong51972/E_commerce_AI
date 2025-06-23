import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from sqlmodel import Session, SQLModel, select

from src import engine
from src.base.model.base_agent_mess_model import BaseAgentMessModel
from src.cache import redis_client
from src.cache.agent_state_cache_wrapper import agent_state_cache_wrapper
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


@agent_state_cache_wrapper
def agent_invoke(agent_state: AgentStateModel) -> AgentStateModel:
    """
    Invoke the AI agent with the provided agent state.
    """
    result = ai_agent.invoke(agent_state)
    processed_state = AgentStateModel.model_validate(result)
    return processed_state


@router.post("/ai_agent")
def ai_agent_v2_api(request: BaseAgentMessModel) -> BaseAgentMessModel:
    """
    Endpoint to handle AI agent requests (v2).
    """
    # Load conversation from cache
    result = agent_invoke(
        AgentStateModel(
            session_id=request.session_id,
            user_id=request.user_id,
            user_input=request.messages,
        )
    )

    response = BaseAgentMessModel(
        user_id=result.user_id,
        session_id=result.session_id,
        messages=(result.messages[-1].content if result.messages else ""),
    )

    return response

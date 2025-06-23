import logging
from functools import wraps

from pydantic import validate_call

from src.cache import redis_client
from src.models.agent.agent_state_model import AgentStateModel
from src.repositories.agent.conversation_repository import (
    load_conversations,
    save_conversation,
)


def agent_state_cache_wrapper(func):
    @wraps(func)
    @validate_call
    def wrapper(agent_state: AgentStateModel):
        cache_key = f"conversation[{agent_state.user_id}:{agent_state.session_id}]"
        cached_agent_state = redis_client.get(cache_key)

        if cached_agent_state:  # Cache hit
            logging.info(f"Cache hit for {cache_key}")
            # Deserialize cached state
            cached_agent_state = AgentStateModel.model_validate_json(cached_agent_state)
        else:  # Cache miss
            logging.info(f"Cache miss for {cache_key}")

            loaded_conversations = load_conversations(
                session_id=agent_state.session_id,
                user_id=agent_state.user_id,
            )
            if loaded_conversations:
                logging.info(f"Loaded conversation from database for {cache_key}")
                cached_agent_state = loaded_conversations
            else:
                logging.info(f"No conversation found in database for {cache_key}")
                cached_agent_state = agent_state

        cached_agent_state.user_input = agent_state.user_input

        result = func(cached_agent_state)

        logging.info(f"Cached {cache_key}")
        redis_client.setex(cache_key, 600, result.model_dump_json())
        number_of_added_messages = len(result.messages) - len(
            cached_agent_state.messages
        )
        save_conversation(
            agent_state=result,
            number_of_last_messages=number_of_added_messages,
        )
        return result

    return wrapper

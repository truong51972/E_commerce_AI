from src.api.agent.agent_api import router as agent_router
from src.api.common.common_api import router as common_router

all_routers = [common_router, agent_router]

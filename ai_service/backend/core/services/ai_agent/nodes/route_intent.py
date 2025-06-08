from core.services.ai_agent.state.agent_state import AgentState


def route_intent(state: AgentState) -> str:
    """
    Function to determine next node based on detected intent.
    """
    intent = state.intent
    if intent == "product":
        return "product"
    elif intent == "greeting":
        return "greeting"
    elif intent == "make_order":
        return "make_order"

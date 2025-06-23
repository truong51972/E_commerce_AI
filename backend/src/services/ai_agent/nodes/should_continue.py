from src.models.agent.agent_state_model import AgentStateModel


# Define the function that determines whether to continue or not
def should_continue(state: AgentStateModel) -> str:
    messages = state.messages
    last_message = messages[-1]
    # If there are no tool calls, then we finish
    if not last_message.tool_calls:
        return "end"
    # Otherwise if there is, we continue
    else:
        return "continue"

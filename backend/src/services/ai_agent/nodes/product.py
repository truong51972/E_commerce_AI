from typing import Any, Dict

from src.base.service.base_agent_service import BaseAgentService

prompt = None
with open("src/services/ai_agent/nodes/prompts/product_v1.md", "r") as f:
    prompt = f.read()


class Product(BaseAgentService):
    agent_prompt: str = prompt
    llm_model: str = "gemini-2.5-flash-preview-05-20"

    def __call__(self, state) -> Dict[str, Any]:
        """
        Handle product-related queries and tool usage
        """
        user_input = state.user_input
        messages = state.messages

        invoke_input = {
            "input": user_input,
            "chat_history": messages,
        }

        response = self.run(invoke_input)

        return {
            "messages": [response],
            "user_input": user_input,
            "intent": state.intent,
        }

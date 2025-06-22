from typing import Any, Dict

from src.base.service.base_agent_service import BaseAgentService

prompt = None
with open("src/services/ai_agent/nodes/prompts/greeting_v1.md", "r") as f:
    prompt = f.read()


class Greeting(BaseAgentService):
    agent_prompt: str = prompt
    llm_model: str = "gemini-2.0-flash-lite"

    def __call__(self, state) -> Dict[str, Any]:
        """
        Phân loại ý định từ 'user_input' trong state và cập nhật state với 'intent' được phát hiện.
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
        }

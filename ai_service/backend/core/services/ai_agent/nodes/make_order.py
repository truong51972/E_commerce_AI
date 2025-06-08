from typing import Any, Dict


from core.base.base_agent import BaseAgent
from core.services.common.tools.make_order_tool import make_order_tool

# prompt hiện có của bạn
prompt = None
with open("core/services/ai_agent/nodes/prompts/make_order_v1.md", "r") as f:
    prompt = f.read()


class MakeOder(BaseAgent):
    agent_prompt: str = prompt
    llm_model: str = "gemini-2.0-flash-lite"
    tools: list = [make_order_tool]

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

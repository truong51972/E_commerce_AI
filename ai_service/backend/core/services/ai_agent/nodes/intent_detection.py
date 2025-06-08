from typing import Any, Dict, Literal

from langchain.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from core.base.base_agent import BaseAgent

list_intents = ["product", "greeting", "make_order"]


class IntentDetectionOutput(BaseModel):
    detected_intent: Literal["product", "greeting", "make_order"]


output_parser = PydanticOutputParser(pydantic_object=IntentDetectionOutput)

prompt = None
with open("core/services/ai_agent/nodes/prompts/intent_detection_v1.md", "r") as f:
    prompt = f.read()


class IntentDetector(BaseAgent):
    llm_model: str = "gemini-2.5-flash-preview-05-20"
    agent_prompt: str = prompt

    def __call__(self, state) -> Dict[str, Any]:
        """
        Phân loại ý định từ 'user_input' trong state và cập nhật state với 'intent' được phát hiện.
        """
        user_input = state.user_input
        messages = state.messages
        if not user_input:
            return {"intent": "greeting", "messages": HumanMessage("")}

        try:
            invoke_input = {
                "input": user_input,
                "list_intents": ", ".join(list_intents),
                "previous_intent": state.intent,
                "chat_history": messages,  # Giả sử state.messages chứa lịch sử trò chuyện
                # "format_instructions": output_parser.get_format_instructions(),
            }

            response = self.run(invoke_input)

            # parsed_output = output_parser.parse(response.content).model_dump()
            # print(f"Parsed output: {parsed_output}")
            # return parsed_output

            detected_intent = response.content.strip().lower()

            # (Tùy chọn) Kiểm tra xem intent có nằm trong danh sách hợp lệ không
            if detected_intent not in list_intents:
                print(
                    f"Cảnh báo: LLM trả về một intent không mong muốn: '{detected_intent}'. Mặc định thành 'orther'."
                )
                detected_intent = "unknown"

            print(f"Input: '{user_input}' - Intent được phát hiện: {detected_intent}")

        except Exception as e:
            print(f"Lỗi trong quá trình phân loại ý định: {e}")
            detected_intent = "greeting"
            state["intent_error"] = str(e)

        return {"intent": detected_intent, "messages": HumanMessage(user_input)}

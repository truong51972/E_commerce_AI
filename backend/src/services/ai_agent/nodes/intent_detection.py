import logging
from typing import Any, Dict, Literal

from langchain.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from src.base.service.base_agent_service import BaseAgentService

list_intents = ["product", "greeting", "make_order"]


class IntentDetectionOutput(BaseModel):
    detected_intent: Literal["product", "greeting", "make_order"]


output_parser = PydanticOutputParser(pydantic_object=IntentDetectionOutput)

prompt = None
with open("src/services/ai_agent/nodes/prompts/intent_detection_v1.md", "r") as f:
    prompt = f.read()


class IntentDetector(BaseAgentService):
    llm_model: str = "gemini-2.5-flash-preview-05-20"
    agent_prompt: str = prompt

    def __call__(self, state) -> Dict[str, Any]:
        """
        Classify intent from 'user_input' in state and update state with detected 'intent'.
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
                "chat_history": messages,  # Assuming state.messages contains chat history
                # "format_instructions": output_parser.get_format_instructions(),
            }

            response = self.run(invoke_input)

            # parsed_output = output_parser.parse(response.content).model_dump()
            # print(f"Parsed output: {parsed_output}")
            # return parsed_output

            detected_intent = response.content.strip().lower()

            # (Optional) Check if intent is in valid list
            if detected_intent not in list_intents:
                logging.warning(
                    f"Warning: LLM returned an unexpected intent: '{detected_intent}'. Defaulting to 'greeting'."
                )
                detected_intent = "greeting"

            logging.info(f"Input: '{user_input}' - Detected intent: {detected_intent}")

        except Exception as e:
            logging.error(f"Error during intent classification: {e}")
            detected_intent = "greeting"
            state["intent_error"] = str(e)

        return {"intent": detected_intent, "messages": HumanMessage(user_input)}

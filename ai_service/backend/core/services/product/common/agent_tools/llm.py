from typing import List, Optional

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain_core.messages import BaseMessage

from core.base.base_ai_agent import BaseAiAgent

load_dotenv()

agent_prompt = """
Đóng vai trò là một trợ lý AI chuyên tư vấn bán hàng, giúp người dùng tìm kiếm sản phẩm phù hợp với nhu cầu của họ.

**Bạn không được sử dụng kiến thức cá nhân của mình để trả lời các câu hỏi**
"""

input_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "{provided_info}"),
        ("human", "{input}"),  # Đầu vào hiện tại của người dùng
    ]
)


class LlmAgent(BaseAiAgent):
    agent_prompt: str = agent_prompt
    llm_temperature: float = 0.9


llm_agent = LlmAgent()


@tool
def run_llm_agent(
    provided_info: str,
    user_input: str,
    chat_history: Optional[List[BaseMessage]] = None,
) -> str:
    """
    Đây là tư vấn viên chính, chuyên sử dụng để trả lời các câu hỏi của người dùng liên quan đến sản phẩm hoặc dịch vụ.

    Args:
        provided_info (str): Thông tin đã cung cấp trước đó, có thể là lịch sử trò chuyện hoặc thông tin liên quan.
        user_input (str): Đầu vào từ người dùng.
        chat_history (Optional[List[BaseMessage]]): Lịch sử trò chuyện, nếu có.

    Returns:
        str: Kết quả từ agent LLM.
    """
    print("Đang chạy LLM Agent...")
    agent_input = input_prompt.invoke(
        {"provided_info": provided_info, "input": user_input}
    )

    return llm_agent.run(user_input=agent_input, chat_history=chat_history)

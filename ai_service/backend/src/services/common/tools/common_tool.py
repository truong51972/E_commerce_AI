import logging

from langchain.tools import tool


@tool
def self_intro_tool(user_input: str) -> str:
    """
    Công cụ để giới thiệu bản thân.
    Bạn sẽ giới thiệu về vai trò của mình là một trợ lý AI chuyên tư vấn bán hàng.
    Args:
        user_input (str): Đầu vào từ người dùng, hỏi về vai trò hoặc mục tiêu của bạn.
    Returns:
        str: Một lời giới thiệu ngắn gọn về vai trò và mục tiêu của bạn.
    """
    logging.info("self_intro_tool called")
    return "Chào bạn! Tôi là trợ lý AI của bạn, chuyên tư vấn bán hàng. Tôi ở đây để giúp bạn tìm kiếm sản phẩm phù hợp với nhu cầu của mình."

import logging
from typing import List, Union

from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_milvus import Milvus
from pydantic import BaseModel, Field, model_validator, validate_call

from src.models.product.product_model import ProductModel

prompt_1 = """
System:
As a customer care and consultation system
you must thinking what user need using <user_input> question and <history> if available
ensure that the output follows <expected_output> format
and your output (include your thinking) MUST answer by <user_input>'s language

<history>
{history}
</history>

User:
<user_input>
{user_input}
</user_input>

Expected output:
<expected_output>
{format_instructions}
</expected_output>
"""

prompt_2 = """
System:
As a customer care and consultation system
you must recommend products
with <user_input>
and based solely on the <context> below
ensure that the output follows <expected_output> format
and your output (include your thinking) MUST answer by <user_input>'s language

<context>
{context}
</context>

<history>
{history}
</history>

<user_input>
{user_input}
</user_input>

Expected output:
<expected_output>
{format_instructions}
</expected_output>
"""


class ChatbotDeepSearch(ProductModel):

    @model_validator(mode="after")
    def __after_init(self):
        return self

    @validate_call
    def extract_info(self, user_input: str, history: str) -> dict:
        class PatternOutput(BaseModel):
            thinking: str = Field(
                description="Brief your thinking of what user's needed, as short as you can"
            )
            keywords: str = Field(
                description="A detailed brief of <user_input> and <history> only for describing a user's needed about a product, including product name if <user_input> mentions it"
            )

        parser = PydanticOutputParser(pydantic_object=PatternOutput)

        retrieval_qa_chat_prompt = ChatPromptTemplate.from_template(
            prompt_1,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        prompt = retrieval_qa_chat_prompt.invoke(
            input={"user_input": user_input, "history": history}
        )
        result = self._llm.invoke(prompt)

        parsed_output = parser.parse(result.content).model_dump()
        return parsed_output

    @validate_call
    def search_docs(self, text: str, k: int = 5):
        milvus = Milvus(
            embedding_function=self._embeddings,
            collection_name=self.collection_name,
            connection_args={"uri": self.milvus_uri, "token": self.milvus_token},
        )

        result = milvus.similarity_search(
            query=text,
            k=k,
        )

        result = [doc.page_content for doc in result]

        return result

    @validate_call
    def augment_answer(self, user_input: str, docs, history: str):
        class PatternOutput(BaseModel):
            answer: str = Field(
                description="Recommended product containing product name, and a brief description, and product link (if available, put it in markdown which anchor text is product name"
            )
            thinking: str = Field(
                description="Brief your thinking of what user's needed with a provided context"
            )

        parser = PydanticOutputParser(pydantic_object=PatternOutput)

        retrieval_qa_chat_prompt = ChatPromptTemplate.from_template(
            prompt_2,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        prompt = retrieval_qa_chat_prompt.invoke(
            input={"user_input": user_input, "context": docs, "history": history}
        )
        result = self._llm.invoke(prompt)

        parsed_output = parser.parse(result.content).model_dump()
        return parsed_output

    @validate_call
    def search(self, user_input: str, history: Union[List[dict], None] = None) -> dict:
        """
        Search for products based on user input and conversation history.
        Args:
            user_input (str): The user's input query.
            history (List[dict]): The conversation history, where each dict contains 'role' and 'content'.
        Returns:
            dict: A dictionary containing the answer, thinking, keywords, and context.

        Example::

            user_input = "Tôi muốn mua một chiếc áo màu xanh"
            history = [
                {"role": "user", "content": "Tôi muốn mua một chiếc áo"},
                {"role": "assistant", "content": "Bạn muốn áo màu gì?"},
            ]

        Example Output::

            {
                "answer": "Tôi nghĩ bạn muốn mua một chiếc áo màu xanh thoải mái.",
                "extract_info_thinking": "Người dùng muốn mua áo màu xanh.",
                "keywords": "áo, màu xanh, thoải mái",
                "docs": "[Áo màu xanh thoải mái]<br>",
                "augment_answer_thinking": "Dựa trên thông tin, tôi nghĩ bạn cần một chiếc áo thoải mái.",
                "context": "áo, màu xanh, thoải mái"
            }

        """
        history_text = ""

        for conversation in history:
            history_text += f"-{conversation['role']}: {conversation['content']}\n"

        extracted_info = self.extract_info(user_input, history_text)

        docs = self.search_docs(extracted_info["keywords"])

        augmented_answer = self.augment_answer(
            user_input=user_input, docs=docs, history=history_text
        )

        text_docs = ""
        for doc in docs:
            text_docs += f"[{repr(doc)}]<br>"

        result = {
            "answer": augmented_answer["answer"],
            "extract_info_thinking": extracted_info["thinking"],
            "keywords": extracted_info["keywords"],
            "docs": text_docs,
            "augment_answer_thinking": augmented_answer["thinking"],
            "context": extracted_info["keywords"],
        }
        return result


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    # langchain.debug = True

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(funcName)s: %(message)s",
    )

    ai_search = ChatbotDeepSearch(collection_name="e_commerce_ai")

    text = "tôi muốn màu xanh"
    history = [
        {"role": "user", "content": "Tôi muốn mua một chiếc áo"},
        {"role": "assistant", "content": "Bạn muốn áo màu gì?"},
    ]
    # context = ["áo, thoải mái"]
    # result = ai_search.extract_info(text, context)
    # result = ai_search.search_docs(context)
    result = ai_search.search(text, history=history)
    # result = ai_search.search(text)

    print(result)

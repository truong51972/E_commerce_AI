import logging

from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_milvus import Milvus
from pydantic import BaseModel, Field, model_validator

from src.models.product.product_model import ProductModel

prompt_1 = """
System:
As a customer care and consultation system
you must thinking what user need using <user_input> question and <context> if available
ensure that the output follows <expected_output> format
and your output (include your thinking) is answer by <user_input>'s language

<context>
{context}
</context>

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
using <keywords> extracted by you before
and based solely on the <context> below
ensure that the output follows <expected_output> format
and your output (include your thinking) is answer by <user_input>'s language

<context>
{context}
</context>

<keywords>
{keywords}
</keywords>

Expected output:
<expected_output>
{format_instructions}
</expected_output>
"""


class ChatbotDeepSearch(ProductModel):

    @model_validator(mode="after")
    def __after_init(self):
        return self

    def extract_info(self, user_input, context):
        class PatternOutput(BaseModel):
            thinking: str = Field(
                description="Brief your thinking of what user's needed, as short as you can"
            )
            keywords: str = Field(
                description="A brief of <user_input> and <context> only for describing a user's needed"
            )

        parser = PydanticOutputParser(pydantic_object=PatternOutput)

        retrieval_qa_chat_prompt = ChatPromptTemplate.from_template(
            prompt_1,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        prompt = retrieval_qa_chat_prompt.invoke(
            input={"user_input": user_input, "context": context}
        )
        result = self._llm.invoke(prompt)

        parsed_output = parser.parse(result.content).model_dump()
        return parsed_output

    def search_docs(self, text, k=5):
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

    def augment_answer(self, keywords, docs):
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
            input={"keywords": keywords, "context": docs}
        )
        result = self._llm.invoke(prompt)

        parsed_output = parser.parse(result.content).model_dump()
        return parsed_output

    def search(self, user_input, context=""):

        extracted_info = self.extract_info(user_input, context)
        # print(extracted_info)
        docs = self.search_docs(extracted_info["keywords"])

        augmented_answer = self.augment_answer(
            keywords=extracted_info["keywords"], docs=docs
        )

        text_docs = ""
        for doc in docs:
            text_docs += f"[{repr(doc)}]<br>"
        # print(augmented_answer)
        result = {
            "answer": augmented_answer["answer"],
            "thinking_1": extracted_info["thinking"],
            "keywords": extracted_info["keywords"],
            # "keywords": augmented_answer["updated_keywords"],
            "docs": text_docs,
            "thinking_2": augmented_answer["thinking"],
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

    ai_search = ChatbotDeepSearch(collection_name="test_08")

    text = "tôi muốn màu xanh"
    context = "áo, thoải mái"
    # result = ai_search.extract_info(text, context)
    result = ai_search.search_docs(context)
    # result = ai_search.search(text, context)

    print(result)

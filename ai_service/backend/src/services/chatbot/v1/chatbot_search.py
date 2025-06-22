from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_milvus import Milvus
from pydantic import BaseModel, Field, model_validator, validate_call

from src.models.product import Product


class ChatbotSearch(Product):

    @model_validator(mode="after")
    def __after_init(self):
        with open("./prompts/ai_search_with_context.txt", "r") as f:
            self._ai_search_with_context_prompt = f.read()

        with open("./prompts/ai_search_with_context__answer.txt", "r") as f:
            self._ai_search_with_context__answer_prompt = f.read()

        with open("./prompts/ai_search_with_context__context.txt", "r") as f:
            self._ai_search_with_context__context_prompt = f.read()
        return self

    @validate_call
    def search(self, text: str, context: str = "") -> dict:
        milvus = Milvus(
            embedding_function=self._embeddings,
            collection_name=self.collection_name,
            connection_args={"uri": self.milvus_uri, "token": self.milvus_token},
        )

        class PatternOutput(BaseModel):
            answer: str = Field(description=self._ai_search_with_context__answer_prompt)
            context: str = Field(
                description=self._ai_search_with_context__context_prompt
            )

        parser = PydanticOutputParser(pydantic_object=PatternOutput)

        retrieval_qa_chat_prompt = ChatPromptTemplate.from_template(
            self._ai_search_with_context_prompt,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        stuff_documents_chain = create_stuff_documents_chain(
            self._llm, retrieval_qa_chat_prompt
        )

        qa = create_retrieval_chain(
            retriever=milvus.as_retriever(),
            combine_docs_chain=stuff_documents_chain,
        )

        text_with_keyword = f"{text}; {context}"
        result = qa.invoke(input={"input": text_with_keyword})
        print(result["answer"])
        parsed_output = parser.parse(result["answer"]).model_dump()
        print(parsed_output)
        return parsed_output

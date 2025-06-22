from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_milvus import Milvus

# for validation
from pydantic import validate_call
from src.models.product import ProductActions


class SearchBasic(ProductActions):

    @validate_call
    def search(self, text: str) -> str:
        milvus = Milvus(
            embedding_function=self._embeddings,
            collection_name=self.collection_name,
            connection_args={"uri": self.milvus_uri, "token": self.milvus_token},
        )

        retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")

        stuff_documents_chain = create_stuff_documents_chain(
            self._llm, retrieval_qa_chat_prompt
        )

        qa = create_retrieval_chain(
            retriever=milvus.as_retriever(),
            combine_docs_chain=stuff_documents_chain,
        )

        result = qa.invoke(input={"input": text})

        return result["answer"]

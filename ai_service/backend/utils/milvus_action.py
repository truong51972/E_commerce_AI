from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_milvus import Milvus
from pydantic import BaseModel, field_validator, Field, model_validator
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
import logging

from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

import langchain
langchain.debug = True  # Bật debug mode


class Milvus_Action(BaseModel):
    milvus_uri: str = Field(default="http://localhost:19530",min_length=10,max_length=100,)
    milvus_token: str = Field(default="root:Milvus", min_length=5, max_length=100)
    collection_name: str = Field(default="default_collection_name", min_length=1, max_length=100)

    embedding_model: str = Field(default="models/text-embedding-004", min_length=5, max_length=100)
    llm_model: str = Field(default="gemini-2.0-flash", min_length=5, max_length=100)

    auto_create_collection: bool = Field(default=True)
    @model_validator(mode="after")
    def after_init(self):
        self.connect_milvus()

        self._embeddings = GoogleGenerativeAIEmbeddings(model=self.embedding_model)
        self._llm = ChatGoogleGenerativeAI(model=self.llm_model)

        if not self.is_collection_exists() and self.auto_create_collection:
            logging.info(f"Creating new collection...")
            self.create_new_collection()

        return self

    def connect_milvus(self):
        if not connections.has_connection('default'):
            logging.info("Connecting to Milvus database...")
            connections.connect(uri=self.milvus_uri, token=self.milvus_token)

    def is_collection_exists(self):
        return utility.has_collection(self.collection_name)

    def is_id_exists(self, id):
        collection = Collection(name=self.collection_name)
        result = collection.query(f"id == {id}")
        return True if result else False

    def create_new_collection(self):
        assert not self.is_collection_exists(), f"'{self.collection_name}' exists!"

        embedding_dim = len(self._embeddings.embed_documents([""])[0])

        fields = [
            FieldSchema(
                name="id", dtype=DataType.INT64, is_primary=True, auto_id=False
            ),
            FieldSchema(name="product_name", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="price", dtype=DataType.DOUBLE),
            FieldSchema(name="description", dtype=DataType.VARCHAR, max_length=16384),
            FieldSchema(
                name="categories",
                dtype=DataType.ARRAY,
                element_type=DataType.VARCHAR,
                max_length=2048,
                max_capacity=50,
            ),
            FieldSchema(name="product_link", dtype=DataType.VARCHAR, max_length=2048),
            FieldSchema(
                name="vector", dtype=DataType.FLOAT_VECTOR, dim=embedding_dim
            ),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=16384),
        ]
        schema = CollectionSchema(fields, description="Product collection with scalar fields")
        collection = Collection(name=self.collection_name, schema=schema)

        index_params = {
            "metric_type": "COSINE",
            "index_type": "HNSW",
            "params": {"M": 8, "efConstruction": 64}
        }
        collection.create_index(field_name="vector", index_params=index_params)

        collection.load()

    def _add_or_edit_record(self, data:dict[str:str]):
        collection = Collection(name=self.collection_name)

        text = "\n".join([
            f"Product Name: {data['product_name']}",
            f"Categories: {data['categories']}"
            f"Description: {data['description']}",
        ])

        vector = self._embeddings.embed_documents([text])[0]

        text += f"\nProduct Link: {data['product_link']}"

        data["vector"] = vector
        data["text"] = text

        collection.insert(data)
        collection.load()

    def add_or_edit_records(self, data: list[dict[str:str]]):
        collection = Collection(name=self.collection_name)
        
        texts = []
        logging.info("Loading data...")
        for record in data:
            text = "\n".join([
                f"Product Name: {record['product_name']}",
                f"Categories: {record['categories']}"
                f"Description: {record['description']}",
            ])

            texts.append(text)

            if isinstance(record["categories"], str):
                record["categories"] = record["categories"].split(', ')

            if isinstance(record["price"], str):
                record["price"] = float(record["price"].replace(",",""))

        logging.info("Embedding...")
        vectors = self._embeddings.embed_documents(texts)

        for i in range(len(data)):
            texts[i] += f"\nProduct Link: {data[i]['product_link']}"

            data[i]["vector"] = vectors[i]
            data[i]["text"] = texts[i]

        logging.info("Loading data into database...")
        collection.insert(data)
        collection.load()
        logging.info("Done!")

    def delete_record(self, id):
        assert self.is_id_exists(id), f"id= {id} does not exist!"
        collection = Collection(name=self.collection_name)

        collection.delete(expr=f"id == {id}")

    def add_new_record(self, data):
        assert self.is_collection_exists(), f"'{self.collection_name}' does not exist!"
        assert not self.is_id_exists(data['id']), f"id= {data['id']} already exists!"

        self._add_or_edit_record(data)

    def edit_record(self, data):
        assert self.is_collection_exists(), f"'{self.collection_name}' does not exist!"
        assert self.is_id_exists(data['id']), f"id={data['id']} does not exist!"

        self._add_or_edit_record(data)

    def get_record(self, id):
        assert self.is_collection_exists(), f"'{self.collection_name}' does not exist!"
        assert self.is_id_exists(id), f"id= {id} does not exist!"

        collection = Collection(name=self.collection_name)

        result = collection.query(
            f"id == {id}",
            output_fields=[
                "id",
                "product_name",
                "description",
                "price",
                "categories",
                "product_link",
            ],
        )[0]

        result['collection_name'] = self.collection_name

        return result

    def quick_search(
        self,
        text,
        price_range: list[float] = [0, 1e9],
        categories: list[str] = ["category_1", "category_2"],
        k: int = 5,
    ):
        assert price_range[0] <= price_range[1], f"Invalid Price Range!"

        milvus = Milvus(
            embedding_function=self._embeddings,
            collection_name=self.collection_name,
            connection_args={"uri": self.milvus_uri, "token": self.milvus_token},
        )

        expr = f"""
                    (price >= {price_range[0]} and price <= {price_range[1]})
                    AND
                    ARRAY_CONTAINS_ALL(categories, {categories})
                """

        result = milvus.similarity_search(
            query=text,
            k=k,
            expr=expr,
        )

        result = [
            {"id": doc.metadata["id"], "product_name": doc.metadata["product_name"]}
            for doc in result
        ]

        return result

    def AI_search(self, text):
        milvus = Milvus(
            embedding_function=self._embeddings,
            collection_name=self.collection_name,
            connection_args={"uri": self.milvus_uri, "token": self.milvus_token},
        )

        retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")

        stuff_documents_chain = create_stuff_documents_chain(self._llm, retrieval_qa_chat_prompt)

        qa = create_retrieval_chain(
            retriever=milvus.as_retriever(),
            combine_docs_chain=stuff_documents_chain,
        )

        result = qa.invoke(input={"input": text})

        return result["answer"]

    def AI_search_with_context(self, text, user_context=""):
        milvus = Milvus(
            embedding_function=self._embeddings,
            collection_name=self.collection_name,
            connection_args={"uri": self.milvus_uri, "token": self.milvus_token},
        )

        class PatternOutput(BaseModel):
            answer: str = Field(description="Recommended product containing product name, and "
                                            "a brief description, and product link (if available)"
            )
            context: str = Field(
                description="List the keywords of <user_input> only "
                            "and keywords have to available in <context>, if not, delete it"
            )

        parser = PydanticOutputParser(pydantic_object=PatternOutput)
        retrieval_qa_chat_prompt = """
System:
As a customer care and consultation system
you must recommend products
using <user_input> question with context
based solely on the <context> below
ensure that the output follows <expected_output> format and answering by <user_input>'s language

<context>
{context}
</context>

User:
<user_input>
{input}
</user_input>

Expected output:
<expected_output>
{format_instructions}
</expected_output>
"""

        retrieval_qa_chat_prompt = ChatPromptTemplate.from_template(
            retrieval_qa_chat_prompt,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        # retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")

        stuff_documents_chain = create_stuff_documents_chain(self._llm, retrieval_qa_chat_prompt)

        qa = create_retrieval_chain(
            retriever=milvus.as_retriever(),
            combine_docs_chain=stuff_documents_chain,
        )

        text_with_keyword = f"{text}; {user_context}"
        result = qa.invoke(input={"input": text_with_keyword})
        parsed_output = parser.parse(result["answer"]).model_dump()
        return parsed_output

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(funcName)s: %(message)s")
    from dotenv import load_dotenv
    import pandas as pd

    load_dotenv()
    # milvus = Milvus_Action(collection_name="clothes_gemini")
    # milvus = Milvus_Action(collection_name="default_collection_name")
    milvus = Milvus_Action(collection_name="test_05")


    df = pd.read_excel("./.data/MLB.xlsx")

    data = df.to_dict(orient="records")

    # print(data[0])

    # data = [
    #     {
    #         "id": 3,
    #         "product_name": "hehe",
    #         "description": "description",
    #         "price": 10,
    #         "categories": ["category_1", "category_2"],
    #         "product_link": "product link",
    #     },
    #     {
    #         "id": 4,
    #         "product_name": "haha",
    #         "description": "description",
    #         "price": 10,
    #         "categories": "category_1, category_3",
    #         "product_link": "product link",
    #     },
    # ]

    milvus.add_or_edit_records(data)
    # milvus.add_new_record(data)
    # milvus.get_record(id=0)

    # print(milvus.AI_search_with_context(text="cho tôi 2 sản phẩm về áo thun tay dài"))

    # user_context = ""
    # while True:
    #     text = input("input: ")
    #     if text.lower() == "q": break

    #     output = milvus.AI_search_with_context(
    #         text=text, user_context=user_context
    #     )

    #     user_context = output["context"]

    #     print(output)
    # milvus.quick_search(text="")
    # milvus.is_id_exists(0)

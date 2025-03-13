import os
import logging
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_milvus import Milvus

from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility


try:
    from backend import settings
    from . import get_texts_from_excel

    MILVUS_URI = settings.MILVUS_URI
    MILVUS_TOKEN = settings.MILVUS_TOKEN
except ImportError:
    import get_texts_from_excel

    MILVUS_URI = "http://localhost:19530"
    MILVUS_TOKEN = "root:Milvus"


def load_from_excel(data_path, collection_name, embeddings):
    logging.info(f"Reading from '{data_path}'!")
    texts = get_texts_from_excel.excel_to_text_list(path=data_path)

    logging.info(f"loaded {len(texts)} documents")
    
    return load_from_texts(texts, collection_name, embeddings, MILVUS_URI, MILVUS_TOKEN)


def load_from_texts(texts, collection_name, embeddings, metadatas):
    logging.info(f"Going to add {len(texts)} to Milvus")
    
    vectorstore = Milvus.from_texts(
        texts,
        embeddings,
        metadatas=metadatas,
        collection_name=collection_name,
        connection_args={"uri": MILVUS_URI, "token": MILVUS_TOKEN},
    )

    logging.info("Loading to vectorstore done!")

    return vectorstore


def is_product_id_exist(id, collection_name, embeddings):
    milvus = Milvus(
        embedding_function=embeddings,
        collection_name=collection_name,
        connection_args={"uri": MILVUS_URI, "token": MILVUS_TOKEN},
    )

    result = milvus.get_pks(expr=f'product_id == {id}')

    return True if result else False


def is_collection_exist(collection_name):
    connections.connect(uri=MILVUS_URI, token=MILVUS_TOKEN)
    exists = utility.has_collection(collection_name)
    
    return exists


def delete_record(id, collection_name, embeddings):
    milvus = Milvus(
        embedding_function=embeddings,
        collection_name=collection_name,
        connection_args={"uri": MILVUS_URI, "token": MILVUS_TOKEN},
    )

    milvus.delete(expr=f'product_id == {id}')


def get_record(id, collection_name, embedding):
    milvus = Milvus(
        embedding_function=embeddings,
        collection_name=collection_name,
        connection_args={"uri": MILVUS_URI, "token": MILVUS_TOKEN},
    )

    result = milvus.similarity_search(
        query="",
        k=1,
        expr=f"product_id == {id}"
    )

    return result[0]


def context_search(
    text,
    collection_name,
    embeddings,
    price_range: list[float] = [-1, -1],
    categories: list[str] = ["category_1"],
    k: int = 5,
):
    if price_range[0] > price_range[1]: assert f"Invalid Price Range!"

    milvus = Milvus(
        embedding_function=embeddings,
        collection_name=collection_name,
        connection_args={"uri": MILVUS_URI, "token": MILVUS_TOKEN},
    )

    expr = ""

    price_expr = ""
    if price_range[0] >= 0 and price_range[1] >= 0:
        price_expr = f"(price >= {price_range[0]} and price <= {price_range[1]})"
    elif price_range[0] >= 0 and price_range[1] < 0:
        price_expr = f"(price >= {price_range[0]})"
    elif price_range[0] < 0 and price_range[1] >= 0:
        price_expr = f"(price <= {price_range[1]})"

    categories_expr = "(" + " OR ".join(categories) + ")"
    
    expr = " AND ".join([price_expr, categories_expr])

    print(expr)
    result = milvus.similarity_search(
        query=text,
        k=k,
        expr=expr
    )

    return [
        {
            "product_name": doc.metadata["product_name"],
            "product_id": doc.metadata["product_id"],
        }
        for doc in result
    ]


if __name__ == "__main__":
    load_dotenv()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    collection_name="default_collection_name"

    load_from_excel(".data/init.xlsx", collection_name, embeddings)
    # milvus = Milvus(
    #     embedding_function=embeddings,
    #     collection_name=collection_name,
    #     connection_args={"uri": MILVUS_URI, "token": MILVUS_TOKEN},
    # )
    
    # print(len(embeddings.embed_documents(["test"])[0]))
    # connections.connect(uri=MILVUS_URI, token=MILVUS_TOKEN)

    # fields = [
    #     FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
    #     FieldSchema(name="price", dtype=DataType.DOUBLE),  # Scalar field cho giá
    #     FieldSchema(name="rating", dtype=DataType.ARRAY, element_type=DataType.VARCHAR, max_capacity=20),  # Scalar field cho đánh giá
    #     FieldSchema(name="category_id", dtype=DataType.INT64),  # Scalar field cho category
    #     FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536)  # Vector embedding
    # ]

    # schema = CollectionSchema(fields, description="Product collection with scalar fields")
    # collection = Collection(name="test1", schema=schema)

    # index_params = {
    #     "metric_type": "COSINE",
    #     "index_type": "HNSW",
    #     "params": {"M": 8, "efConstruction": 64}
    # }
    # collection.create_index(field_name="embedding", index_params=index_params)

    # collection.load()

    # result = milvus.get_pks(expr=f'pk == 456503865730138237')
    # result = is_collection_exist(collection_name, embeddings)
    # print(result)
    # result = milvus.similarity_search(
    #     query="",
    #     k=1,
    #     expr=r'categories LIKE "%[category_1]%"'
    # )
    # result = context_search(
    #     text="test",
    #     collection_name=collection_name,
    #     embeddings=embeddings
    # )

    # for doc in result:
    # print(doc.metadata["product_id"])
    # print(result)

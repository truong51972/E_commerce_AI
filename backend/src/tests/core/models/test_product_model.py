import dotenv
import pandas as pd
import pytest
from pymilvus import utility

from src.base.service.base_milvus_service import BaseMilvusService
from src.models.product.product_model import ProductModel

dotenv.load_dotenv()


collection_name = "test_product_collection"
llm_model = "gemini-2.0-flash"
milvus_uri = "http://localhost:19530"
milvus_token = "root:Milvus"


@pytest.fixture(scope="module", autouse=True)
def setup_milvus_collection():
    # check if the collection already exists and delete it
    BaseMilvusService(
        collection_name=collection_name,
        milvus_uri=milvus_uri,
        milvus_token=milvus_token,
    )

    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)


def test_product_model_initialization():
    """Test the initialization of the ProductModel class."""

    # Initialize the ProductModel with test parameters

    product_model = ProductModel(
        collection_name=collection_name,
        llm_model=llm_model,
        milvus_uri=milvus_uri,
        milvus_token=milvus_token,
    )

    assert product_model.collection_name == collection_name
    assert product_model.llm_model == llm_model
    assert product_model.milvus_uri == milvus_uri
    assert product_model.milvus_token == milvus_token

    # utility.drop_collection(collection_name)


def test_product_model_create():
    """Test the create method of the ProductModel class."""

    product_model = ProductModel(
        collection_name=collection_name,
        llm_model=llm_model,
        milvus_uri=milvus_uri,
        milvus_token=milvus_token,
    )

    df = pd.read_excel("src/tests/src/models/data_test.xlsx")

    df.columns = df.columns.str.lower()

    data = df.to_dict(orient="records")

    product_model.create_records(data)

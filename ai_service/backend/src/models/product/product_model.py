import hashlib
from typing import List, Optional

# for validation
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
    validate_call,
)
from pymilvus import DataType


@validate_call
def create_unique_id(text: str = Field(min_length=1)) -> int:
    """Create a unique id with text as a seed"""
    # assert len(text) < 1000, "text must not be too long"

    # create a unique id for the product
    hash_bytes = hashlib.md5(text.encode()).digest()
    int_64bit = int.from_bytes(hash_bytes[:8], "big", signed=True)  # Dạng signed
    return int_64bit


class ProductModel(BaseModel):
    """Product model"""

    id: int = Field(
        default=None,
        description="product ID, must be unique.",
        json_schema_extra={
            "milvus_config": {
                "dtype": DataType.INT64,
                "is_primary": True,
                "auto_id": False,
            },
        },
    )

    product_name: str = Field(
        min_length=3,
        max_length=512,
        description="product name",
        json_schema_extra={
            "milvus_config": {
                "dtype": DataType.VARCHAR,
                "max_length": 512,  # Milvus VARCHAR max_length
            }
        },
    )

    price: float = Field(
        gt=0,
        description="price of the product, must be greater than 0.",
        json_schema_extra={
            "milvus_config": {
                "dtype": DataType.DOUBLE,
            }
        },
    )

    description: str = Field(
        min_length=10,
        description="product description, must be at least 10 characters long.",
        json_schema_extra={
            "milvus_config": {
                "dtype": DataType.VARCHAR,
                "max_length": 16384,  # Milvus VARCHAR max_length
            }
        },
    )

    product_link: str = Field(
        # pattern=r"^https?://.*",  # Pydantic regex validation
        description="product link, must be a valid URL.",
        json_schema_extra={
            "milvus_config": {
                "dtype": DataType.VARCHAR,
                "max_length": 2048,  # Milvus VARCHAR max_length
            }
        },
    )

    category_tier_one: Optional[str] = Field(
        default_factory=str,
        description="Category tier one, used for categorization.",
        json_schema_extra={
            "milvus_config": {
                "dtype": DataType.VARCHAR,
                "max_length": 512,  # Milvus VARCHAR max_length
            }
        },
    )

    category_tier_two: Optional[str] = Field(
        default_factory=str,
        description="Category tier two, used for categorization.",
        json_schema_extra={
            "milvus_config": {
                "dtype": DataType.VARCHAR,
                "max_length": 512,  # Milvus VARCHAR max_length
            }
        },
    )

    category_tier_three: Optional[str] = Field(
        default_factory=str,
        description="Category tier three, used for categorization.",
        json_schema_extra={
            "milvus_config": {
                "dtype": DataType.VARCHAR,
                "max_length": 512,  # Milvus VARCHAR max_length
            }
        },
    )

    vector: Optional[List[float]] = Field(
        default_factory=list,
        description="embedding vector for the product, must be a list of floats.",
        json_schema_extra={
            "milvus_config": {
                "dtype": DataType.FLOAT_VECTOR
                # 'dim' will be dynamically added from the 'embedding_dim' parameter
            }
        },
    )

    text: Optional[str] = Field(
        default_factory=str,
        description="text for context, used for displaying product information.",
        json_schema_extra={
            "milvus_config": {
                "dtype": DataType.VARCHAR,
                "max_length": 16384,  # Milvus VARCHAR max_length
            }
        },
    )

    text_for_embedding: Optional[str] = Field(
        default_factory=str,
        exclude=True,  # exclude from model while converting to dict
        description="embedding text, used for generating the vector.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "product_name": "Product Name",
                "price": 100.0,
                "description": "Product Description",
                "category_tier_one": "Category Tier One",
                "category_tier_two": "Category Tier Two",
                "category_tier_three": "Category Tier Three",
                "product_link": "https://example.com/product/1",
            }
        }
    )

    # check price, if not float, try to convert to float
    @field_validator("price", mode="before")
    def check_price(cls, v):
        if isinstance(v, str):
            try:
                v = float(v.replace(",", ""))
            except ValueError:
                raise ValueError(
                    "Price must be a float or a string that can be converted to a float"
                )
        return v

    # after init, create a new text for embedding
    @model_validator(mode="after")
    def create_text_for_embedding(self):
        # create a new text for embedding
        self.text_for_embedding = "\n".join(
            [
                f"Product Name: {self.product_name}",
                f"Price: {self.price}",
                f"Categories: {self.category_tier_one}, {self.category_tier_two}, {self.category_tier_three}",
                f"Description: {self.description}",
            ]
        )
        return self

    # after init, create a new text for context
    @model_validator(mode="after")
    def create_text(self):
        # create a new text for context
        self.text = "\n".join(
            [
                f"Product Name: {self.product_name}",
                f"Price: {self.price}",
                f"Categories: {self.category_tier_one}, {self.category_tier_two}, {self.category_tier_three}",
                f"Description: {self.description}",
                f"Product Link: {self.product_link}",
            ]
        )
        return self

    # after init, if id not exists, create a new id from defined seed
    @model_validator(mode="after")
    def check_id(self):
        if self.id is None:
            # create a new id from defined seed
            seed = self.description + self.product_name + self.product_link
            if seed:
                self.id = create_unique_id(seed)
            else:
                raise ValueError(
                    "ID must be provided or text must be provided to create a new ID"
                )
        return self

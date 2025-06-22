from typing import List, Type

from pydantic import BaseModel
from pymilvus import DataType, FieldSchema


def generate_milvus_field_schemas_from_pydantic(
    pydantic_model: Type[BaseModel],
    embedding_dim: int,  # The embedding_dim parameter is passed here
) -> List[FieldSchema]:
    """
    Generates a list of Milvus FieldSchema objects from a Pydantic BaseModel.

    Args:
        pydantic_model: The Pydantic BaseModel class containing field definitions.
        embedding_dim: The dimension of the embedding vector, required for FLOAT_VECTOR fields.

    Returns:
        A list of FieldSchema objects corresponding to Milvus.

    Raises:
        ValueError: If Milvus configuration is invalid or missing.
    """

    fields = []

    # Iterate through all fields defined in the Pydantic Model
    for field_name, model_field in pydantic_model.model_fields.items():
        # Check if the field has 'exclude=True' in its extra info
        # If so, this field should not be included in the Milvus schema
        if model_field.json_schema_extra and model_field.json_schema_extra.get(
            "exclude", False
        ):
            continue

        # Check if the field has json_schema_extra with milvus_config
        if not model_field.json_schema_extra:
            continue

        # Get the milvus_config dictionary from json_schema_extra
        milvus_config = model_field.json_schema_extra.get("milvus_config")

        # If no milvus_config is found, skip this field (it's not for Milvus)
        if not milvus_config:
            continue

        # Get the dtype (mandatory for Milvus fields)
        dtype = milvus_config.get("dtype")
        if not dtype:
            raise ValueError(
                f"Missing 'dtype' in milvus_config for field '{field_name}'."
            )

        # Initialize dictionary to build parameters for FieldSchema
        milvus_field_params = {
            "name": field_name,
            "dtype": dtype,
        }

        # Add description if available in Pydantic Field
        if model_field.description:
            milvus_field_params["description"] = model_field.description

        # Handle common FieldSchema attributes
        if "is_primary" in milvus_config:
            milvus_field_params["is_primary"] = milvus_config["is_primary"]
        if "auto_id" in milvus_config:
            milvus_field_params["auto_id"] = milvus_config["auto_id"]

        # Handle specific parameters based on Milvus DataType
        if dtype == DataType.VARCHAR:
            milvus_field_params["max_length"] = milvus_config.get("max_length", 256)

        elif dtype == DataType.ARRAY:
            milvus_field_params["element_type"] = milvus_config.get("element_type")
            milvus_field_params["max_length"] = milvus_config.get("max_length", 1024)
            milvus_field_params["max_capacity"] = milvus_config.get("max_capacity", 128)
            if not milvus_field_params["element_type"]:
                raise ValueError(
                    f"Missing 'element_type' for ARRAY field '{field_name}'."
                )
        elif dtype == DataType.FLOAT_VECTOR:
            # The 'dim' parameter is taken from the embedding_dim passed to the function
            milvus_field_params["dim"] = embedding_dim
            # You can add validation here for embedding_dim if needed
            if not isinstance(embedding_dim, int) or embedding_dim <= 0:
                raise ValueError(
                    f"Invalid 'embedding_dim' for FLOAT_VECTOR field '{field_name}'. Must be a positive integer."
                )

        # Add any other Milvus FieldSchema attributes defined in milvus_config
        # that are not already handled above (dtype, is_primary, auto_id, max_length, etc.)
        # This is a catch-all if you add a new attribute without specific logic
        for key, value in milvus_config.items():
            if key not in milvus_field_params and key not in [
                "dtype",
                "element_type",
                "max_length",
                "max_capacity",
                "dim",
                "is_primary",
                "auto_id",
            ]:
                milvus_field_params[key] = value

        # Create the FieldSchema object and add it to the list
        fields.append(FieldSchema(**milvus_field_params))

    return fields


# --- Example Usage ---
if __name__ == "__main__":
    from src.models.product import ProductSchema  # Example path

    EMBEDDING_DIMENSION = 768  # Assume your embedding size

    milvus_fields = generate_milvus_field_schemas_from_pydantic(
        ProductSchema, embedding_dim=EMBEDDING_DIMENSION
    )

    print("Generated Milvus Field Schemas:")
    for field in milvus_fields:
        print(
            f"  - Name: {field.name}, Dtype: {field.dtype}, Params: {field.params}, Primary: {field.is_primary}"
        )

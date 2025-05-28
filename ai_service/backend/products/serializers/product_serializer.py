from rest_framework import serializers
from drf_pydantic import BaseModel as DRFBaseModel
from drf_pydantic.base_serializer import DrfPydanticSerializer
from core.rag.models.product import ProductSchema


class ProductSerializer(DrfPydanticSerializer):
    __schema__ = ProductSchema
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
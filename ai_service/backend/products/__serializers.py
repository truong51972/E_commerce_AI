import json

from rest_framework import serializers

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from core.rag.models.product import Product


embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

class ProductionVectorRecordSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    product_name = serializers.CharField(default="Product Name")
    description = serializers.CharField(default="This is the Product's Description, Bla bla bla...")
    price = serializers.FloatField()
    categories = serializers.ListField(
        child=serializers.CharField(),
        default=["category_1", "category_2", "category_3"]
    )
    product_link = serializers.CharField(default="https://example.com/")
    collection_name = serializers.CharField(default="default_collection_name")

    # def is_id_exists(self):
    #     milvus = Product(collection_name=)


    def create(self, validated_data:dict):
        """
        Create and return a new `Record` instance, given the validated data.
        """
        data = validated_data
        collection_name = data.pop("collection_name")

        milvus = Product(collection_name=collection_name)

        if milvus.is_id_exists(id=data['id']):
            raise serializers.ValidationError("Id already exists!")

        milvus.add_new_record(data=data)
        return validated_data

    def update(self, instance, validated_data):
        """
        Update and return an existing `Record` instance, given the validated data.
        """
        data = validated_data
        collection_name = data.pop("collection_name")
        milvus = Product(collection_name=collection_name)

        if not milvus.is_id_exists(id=data['id']):
            raise serializers.ValidationError("Id dose not exist!")

        milvus.edit_record(data=data)
        return instance


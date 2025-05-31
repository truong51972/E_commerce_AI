from django.contrib.auth.models import Group, User
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from rest_framework import permissions, viewsets, status

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from ..serializers import product_serializer

from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from core.models.product import ProductSchema


class ProductViewSet(viewsets.ViewSet):

    @extend_schema(
        request=product_serializer.ProductSchema,
    )
    def create(self, request): # HTTP POST
        """
        Create a product record
        """
        data = request.data

        serializer = product_serializer.ProductSerializer(data=data)
        if not serializer.is_valid():
            return Response({"message": "Invalid Data!", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    @action(detail=False, methods=['put'], url_path='update')
    def update_no_pk(self, request):  # HTTP PUT
        """
        Update a record
        """
        data = request.data
        id = data["id"]
        collection_name = data["collection_name"]

        milvus = Milvus_Action(collection_name=collection_name)
        record = milvus.get_record(id=id)

        serializer = product_serializer.ProductSerializer(record, data=data)
        if not serializer.is_valid():
            return Response({"message": "Invalid Data!", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    
    def retrieve(self, request, pk):
        """
        Get a record
        """
        collection_name = request.query_params.get("collection_name")

        milvus = Product(collection_name=collection_name, auto_create_collection=False)

        if not milvus.is_collection_exists():
            return Response({"message": "Collection does not exist!"}, status=status.HTTP_404_NOT_FOUND)

        if not milvus.is_id_exists(id=pk):
            return Response({"message": "ID not found"}, status=status.HTTP_404_NOT_FOUND)

        record = milvus.get_record(id=pk)
        serializer = product_serializer.ProductSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    def destroy(self, request, pk=None): 
        """
        docs 3
        """
        collection_name = request.query_params.get("collection_name")

        milvus = Product(collection_name=collection_name, auto_create_collection=False)

        if not milvus.is_collection_exists():
            return Response({"message": "Collection does not exist!"}, status=status.HTTP_404_NOT_FOUND)

        if not milvus.is_id_exists(id=pk):
            return Response({"message": "ID not found"}, status=status.HTTP_404_NOT_FOUND)

        milvus.delete_record(pk)
        
        return Response({"message": "Deleted successfully!"}, status=status.HTTP_202_ACCEPTED)


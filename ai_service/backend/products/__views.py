from django.contrib.auth.models import Group, User
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from rest_framework import permissions, viewsets, status

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from . import __serializers

from rest_framework.decorators import action

from core.rag.milvus_action import Milvus_Action

from core.rag.models.product import Products

from core.rag.services.quick_search import QuickSearch
from core.rag.services.ai_search import AiSearch
from core.rag.services.ai_search_with_context import AiSearchWithContext



class ProductionVectorRecordViewSet(viewsets.ViewSet):
    """
    docs 1
    """
    @swagger_auto_schema(
        request_body=__serializers.ProductionVectorRecordSerializer,
        responses={
            201: openapi.Response(
                "Record is created!", __serializers.ProductionVectorRecordSerializer, None
            ),
            400: openapi.Response(
                "Invalid Data",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="message",
                            default="Invalid Data!",
                        )
                    },
                ),
            ),
        },
        tags=["Product Record"],
        operation_id="Create a new product record",
    )
    def create(self, request): # HTTP POST
        """
        Create a product record
        """
        data = request.data

        serializer = __serializers.ProductionVectorRecordSerializer(data=data)
        if not serializer.is_valid():
            return Response({"message": "Invalid Data!", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=__serializers.ProductionVectorRecordSerializer,
        responses={
            202: openapi.Response(
                "Record is updated!", __serializers.ProductionVectorRecordSerializer, None
            ),
            400: openapi.Response(
                "Invalid Data",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="message",
                            default="Invalid Data!",
                        )
                    },
                ),
            ),
        },
        tags=["Product Record"],
        operation_id="Update a product record",
    )
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

        serializer = __serializers.ProductionVectorRecordSerializer(record, data=data)
        if not serializer.is_valid():
            return Response({"message": "Invalid Data!", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "collection_name",
                openapi.IN_QUERY,
                description="Collection Name",
                type=openapi.TYPE_STRING,
                default="default_collection_name",
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                "Okie!", __serializers.ProductionVectorRecordSerializer, None
            ),
            404: openapi.Response(
                "Invalid data",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="message",
                            default="Id/Collection dose not exist!!",
                        )
                    },
                ),
            ),
        },
        tags=["Product Record"],
        operation_id="Retrieve a product record",
    )
    def retrieve(self, request, pk):
        """
        Get a record
        """
        collection_name = request.query_params.get("collection_name")

        milvus = Products(collection_name=collection_name, auto_create_collection=False)

        if not milvus.is_collection_exists():
            return Response({"message": "Collection does not exist!"}, status=status.HTTP_404_NOT_FOUND)

        if not milvus.is_id_exists(id=pk):
            return Response({"message": "ID not found"}, status=status.HTTP_404_NOT_FOUND)

        record = milvus.get_record(id=pk)
        serializer = __serializers.ProductionVectorRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "collection_name",
                openapi.IN_QUERY,
                description="Collection Name",
                type=openapi.TYPE_STRING,
                default="default_collection_name",
                required=True,
            ),
        ],
        responses={
            204: openapi.Response(
                "Deleted successfully!",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="message",
                            default="Deleted successfully!",
                        )
                    },
                ),
            ),
            400: openapi.Response(
                "Invalid Data!",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="message",
                            default="collection_name required!",
                        )
                    },
                ),
            ),
            404: openapi.Response(
                "Invalid Data!",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="message",
                            default="Id/Collection dose not exist!",
                        )
                    },
                ),
            ),
            # 401: "Unauthorized - Yêu cầu đăng nhập",
            # 500: openapi.Response("Lỗi server"),
        },
        tags=["Product Record"],
        operation_id="Delete product record if exist",
    )
    def destroy(self, request, pk=None): 
        """
        docs 3
        """
        collection_name = request.query_params.get("collection_name")

        milvus = Products(collection_name=collection_name, auto_create_collection=False)

        if not milvus.is_collection_exists():
            return Response({"message": "Collection does not exist!"}, status=status.HTTP_404_NOT_FOUND)

        if not milvus.is_id_exists(id=pk):
            return Response({"message": "ID not found"}, status=status.HTTP_404_NOT_FOUND)

        milvus.delete_record(pk)
        
        return Response({"message": "Deleted successfully!"}, status=status.HTTP_202_ACCEPTED)


class QuickSearchAPIView(APIView):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "text": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="text",
                    default="Text query",
                ),
                "collection_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="collection_name",
                    default="default_collection_name",
                ),
                "price_range": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="Price range (min, max) in float",
                    items=openapi.Items(
                        type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT
                    ),
                    default=[0, 1e9],
                ),
                "categories": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="Categories of product",
                    items=openapi.Items(
                        type=openapi.TYPE_STRING, format=openapi.FORMAT_FLOAT
                    ),
                    default=["category_1", "category_2"],
                ),
                "k": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Number of output",
                    default=5,
                ),
            },
            required=["text", "collection_name"],
        ),
        responses={
            200: openapi.Response(
                "List of product name and id",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "products": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            description="Price range (min, max) in float",
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "product_name": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="product_name",
                                        default="Product Name",
                                    ),
                                    "id": openapi.Schema(
                                        type=openapi.TYPE_INTEGER,
                                        description="Number of output",
                                        default=0,
                                    ),
                                },
                            ),
                        ),
                    },
                ),
            ),
            404: openapi.Response(
                "Invalid Data!",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="message",
                            default="Collection does not exist!",
                        )
                    },
                ),
            ),
        },
        tags=["Search engine"],
        operation_id="Quick Search",
    )
    def post(self, request):
        """Context search"""
        collection_name = request.data["collection_name"]
        text = request.data["text"]
        price_range = request.data["price_range"]
        categories = request.data["categories"]
        k = request.data["k"]

        milvus = QuickSearch(collection_name=collection_name, auto_create_collection=False)

        if not milvus.is_collection_exists():
            return Response({"message": "Collection does not exist!"}, status=status.HTTP_404_NOT_FOUND)

        result = milvus.search(
            text=text,
            price_range=price_range,
            categories=categories,
            k=k
        )

        return Response(result, status=status.HTTP_200_OK)


class AiSearchAPIView(APIView):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "text": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="text",
                    default="Text query",
                ),
                "collection_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="collection_name",
                    default="default_collection_name",
                ),
            },
            required=["text", "collection_name"],
        ),
        responses={
            200: openapi.Response(
                "List of product name and id",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "text": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="text",
                            default="Text query",
                        ),
                    },
                ),
            ),
            404: openapi.Response(
                "Invalid Data!",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="message",
                            default="Collection does not exist!",
                        )
                    },
                ),
            ),
        },
        tags=["Search engine"],
        operation_id="AI Search",
    )
    def post(self, request):
        """Agent search"""
        collection_name = request.data["collection_name"]
        text = request.data["text"]

        milvus = AiSearch(collection_name=collection_name, auto_create_collection=False)

        if not milvus.is_collection_exists():
            return Response({"message": "Collection does not exist!"}, status=status.HTTP_404_NOT_FOUND)

        result = milvus.search(
            text=text,
        )

        return Response({"text": result}, status=status.HTTP_200_OK)


class AiSearchWithContextAPIView(APIView):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "text": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="text",
                    default="Text query",
                ),
                "context": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="context",
                    default="context query",
                ),
                "collection_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="collection_name",
                    default="default_collection_name",
                ),
            },
            required=["text", "collection_name"],
        ),
        responses={
            200: openapi.Response(
                "List of product name and id",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "text": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="text",
                            default="Text query",
                        ),
                    },
                ),
            ),
            404: openapi.Response(
                "Invalid Data!",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="message",
                            default="Collection does not exist!",
                        )
                    },
                ),
            ),
        },
        tags=["Search engine"],
        operation_id="AI Search with Context",
    )
    def post(self, request):
        """Agent search"""
        collection_name = request.data["collection_name"]
        text = request.data["text"]
        context = request.data["context"]

        milvus = AiSearchWithContext(collection_name=collection_name, auto_create_collection=False)

        if not milvus.is_collection_exists():
            return Response({"message": "Collection does not exist!"}, status=status.HTTP_404_NOT_FOUND)

        result = milvus.search(
            text=text,
            context=context
        )

        return Response({"text": result}, status=status.HTTP_200_OK)
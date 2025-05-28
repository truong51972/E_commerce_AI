class SearchAdvancedAPIView(APIView):

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

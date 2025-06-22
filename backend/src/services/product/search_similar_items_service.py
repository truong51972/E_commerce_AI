import logging
from typing import List

# for validation
from pydantic import Field, validate_call
from pymilvus import Collection
from src.models.product import Product


class SearchSimilarItems(Product):

    @validate_call
    def search(
        self,
        ids: List[int] = Field(
            ...,
            min_length=1,
            max_length=20,
            description="List of product ids to search for similar products.",
        ),
        output_num: int = Field(
            5,
            gt=0,
            description="Number of similar products to return. Defaults to 5 and must be greater than 0.",
        ),
    ) -> List[int] | None:
        """
        Search for products similar to the given ids.
        Args:
            ids (list[int]): List of product ids to search for similar products.
            output_num (int): Number of similar products to return. Defaults to 5.
        Returns:
            list[int]: List of product ids of similar products.
        """
        # Validate input

        collection = Collection(name=self.collection_name)

        query_results = collection.query(
            expr=f"id IN {ids}", output_fields=["id", "vector"]
        )

        search_params = {
            "metric_type": "COSINE",
            "params": {
                "ef": 64,
                "radius": 0.90,  # only take results with cosine similarity > radius
            },
        }

        search_results = collection.search(
            data=[res["vector"] for res in query_results],
            anns_field="vector",
            param=search_params,
            limit=output_num + 1,  # +1 to get the top K results
            output_fields=["id"],
            expr=f"id NOT IN {ids}",
        )

        combined_search_results = []
        combined_search_ids = set()
        # combine results from multiple queries
        for hits in search_results:
            for hit in hits:
                # avoid duplicates
                # if the hit id is not already in combined_search_ids, add it
                if hit.id not in combined_search_ids:
                    combined_search_ids.add(hit.id)
                    combined_search_results.append(hit)

        # sort results by ssrc (cosine similarity)
        sorted_search_results = sorted(
            combined_search_results, key=lambda x: x.distance, reverse=True
        )

        # limit the results to output_num
        if len(sorted_search_results) > output_num:
            sorted_search_results = sorted_search_results[:output_num]

        # return only the ids of the search results
        return sorted_search_results


if __name__ == "__main__":
    from dotenv import load_dotenv
    from src.models.product import Product

    load_dotenv()

    # langchain.debug = True

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(funcName)s: %(message)s",
    )

    rs = SearchSimilarItems(collection_name="e_commerce_ai")
    products = Product(collection_name="e_commerce_ai")
    res = rs.search(
        ids=[-6554713162909277892, -3354522976921633338, -1530099612076136296]
    )

    print("Search results:", res)
    print()
    for id in res:
        record = products.get_record(id=id)
        print(
            f"Product ID: {id}, Name: {record['product_name']}, Price: {record['price']}"
        )

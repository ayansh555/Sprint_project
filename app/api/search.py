from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.database.models import Product

from app.schemas.search import SearchRequest

from app.services.semantic_search import (
    SemanticSearch
)

from app.services.gemini_service import (
    interpret_query
)


router = APIRouter(
    prefix="/search",
    tags=["Search"]
)


semantic_search = SemanticSearch()


@router.post("/")
def search_products(
    request: SearchRequest,
    db: Session = Depends(get_db)
):

    query = request.query


    # ---------------------------------
    # GEMINI QUERY INTERPRETATION
    # ---------------------------------

    try:

        interpreted_query = (
            interpret_query(query)
        )

    except Exception as e:

        interpreted_query = (
            "Gemini interpretation unavailable."
        )


    # ---------------------------------
    # SEMANTIC SEARCH
    # ---------------------------------

    search_results = (
        semantic_search.search(
            query=query,
            top_k=request.top_k
        )
    )


    # ---------------------------------
    # GET PRODUCT IDs
    # ---------------------------------

    product_ids = [

        result["product_id"]

        for result in search_results

    ]


    if not product_ids:

        return {

            "query": query,

            "interpreted_query":
                interpreted_query,

            "results": []

        }


    # ---------------------------------
    # GET PRODUCTS FROM POSTGRESQL
    # ---------------------------------

    products = (
        db.query(Product)

        .filter(
            Product.product_id.in_(
                product_ids
            )
        )

        .all()
    )


    product_map = {

        product.product_id:
            product

        for product in products

    }


    # ---------------------------------
    # COMBINE RESULTS
    # ---------------------------------

    results = []


    for result in search_results:

        product = product_map.get(
            result["product_id"]
        )


        if not product:

            continue


        results.append(

            {

                "product_id":
                    product.product_id,

                "product_name":
                    product.product_name,

                "brand":
                    product.brand,

                "category":
                    product.category,

                "description":
                    product.description,

                "price":
                    product.price,

                "rating":
                    product.rating,

                "similarity_score":
                    result[
                        "similarity_score"
                    ]

            }

        )


    return {

        "query": query,

        "interpreted_query":
            interpreted_query,

        "results": results

    }
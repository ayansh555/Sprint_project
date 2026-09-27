from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Product
from app.schemas.search import SearchRequest
from app.services.semantic_search import SemanticSearch
from app.services.gemini_service import interpret_query


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

    # ========================================================
    # GEMINI QUERY INTERPRETATION
    # ========================================================

    try:

        interpreted_query = interpret_query(query)

    except Exception:

        interpreted_query = (
            "Gemini interpretation unavailable."
        )


    # ========================================================
    # SEMANTIC SEARCH
    # ========================================================

    search_limit = max(
        request.top_k * 5,
        40
    )

    search_results = semantic_search.search(
        query=query,
        top_k=search_limit
    )


    product_ids = [
        result["product_id"]
        for result in search_results
    ]


    if not product_ids:

        return {
            "query": query,
            "interpreted_query": interpreted_query,
            "results": []
        }


    # ========================================================
    # GET PRODUCTS FROM POSTGRESQL
    # ========================================================

    products = (
        db.query(Product)
        .filter(
            Product.product_id.in_(product_ids)
        )
        .all()
    )


    product_map = {
        product.product_id: product
        for product in products
    }


    # ========================================================
    # BUILD CANDIDATES
    # ========================================================

    candidates = []


    for result in search_results:

        product = product_map.get(
            result["product_id"]
        )


        if not product:
            continue


        candidates.append({

            "product": product,

            "similarity_score":
                result["similarity_score"]

        })


    # ========================================================
    # PRODUCTS WITH MEDIA / LINKS
    # ========================================================

    products_with_media = [

        item

        for item in candidates

        if (
            item["product"].image_url
            or
            item["product"].amazon_url
            or
            item["product"].product_url
            or
            item["product"].flipkart_url
            or
            item["product"].croma_url
            or
            item["product"].myntra_url
        )

    ]


    products_without_media = [

        item

        for item in candidates

        if not (
            item["product"].image_url
            or
            item["product"].amazon_url
            or
            item["product"].product_url
            or
            item["product"].flipkart_url
            or
            item["product"].croma_url
            or
            item["product"].myntra_url
        )

    ]


    # ========================================================
    # COMBINE RESULTS
    # ========================================================

    selected_candidates = (
        products_with_media +
        products_without_media
    )


    selected_candidates = selected_candidates[
        :request.top_k
    ]


    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    results = []


    for item in selected_candidates:

        product = item["product"]

        results.append({

            # ------------------------------------------------
            # Basic information
            # ------------------------------------------------

            "product_id":
                product.product_id,

            "product_name":
                product.product_name,

            "brand":
                product.brand,

            "category":
                product.category,


            # ------------------------------------------------
            # Product details
            # ------------------------------------------------

            "description":
                product.description,

            "user_reviews":
                product.user_reviews,


            # ------------------------------------------------
            # Metrics
            # ------------------------------------------------

            "price":
                product.price,

            "rating":
                product.rating,

            "quantity_sold":
                product.quantity_sold,

            "recommendation_score":
                product.recommendation_score,


            # ------------------------------------------------
            # Image
            # ------------------------------------------------

            "image_url":
                product.image_url,


            # ------------------------------------------------
            # Product URL
            # ------------------------------------------------

            "product_url":
                product.product_url,


            # ------------------------------------------------
            # Retailer URLs
            # ------------------------------------------------

            "amazon_url":
                product.amazon_url,

            "flipkart_url":
                product.flipkart_url,

            "croma_url":
                product.croma_url,

            "myntra_url":
                product.myntra_url,

            "reliance_url":
                product.reliance_url,

            "official_url":
                product.official_url,


            # ------------------------------------------------
            # Semantic similarity
            # ------------------------------------------------

            "similarity_score":
                item["similarity_score"]

        })


    return {

        "query":
            query,

        "interpreted_query":
            interpreted_query,

        "results":
            results

    }
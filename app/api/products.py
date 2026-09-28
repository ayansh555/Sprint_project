from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Product


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# ============================================================
# PRODUCT RESPONSE HELPER
# ============================================================

def product_to_dict(product: Product):
    return {
        "product_id": product.product_id,
        "product_name": product.product_name,
        "brand": product.brand,
        "category": product.category,
        "description": product.description,
        "user_reviews": product.user_reviews,
        "price": product.price,
        "rating": product.rating,
        "quantity_sold": product.quantity_sold,
        "recommendation_score": product.recommendation_score,

        # Product image
        "image_url": product.image_url,

        # Main product page
        "product_url": product.product_url,

        # Retailer links
        "amazon_url": product.amazon_url,
        "flipkart_url": product.flipkart_url,
        "croma_url": product.croma_url,
        "myntra_url": product.myntra_url,
        "reliance_url": product.reliance_url,
        "official_url": product.official_url,
    }


# ============================================================
# GET PRODUCTS
# ============================================================

@router.get("/")
def get_products(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Return a list of products.
    """

    limit = min(
        max(limit, 1),
        100
    )

    products = (
        db.query(Product)
        .limit(limit)
        .all()
    )

    return [
        product_to_dict(product)
        for product in products
    ]


# ============================================================
# GET SINGLE PRODUCT
# ============================================================

@router.get("/{product_id}")
def get_product(
    product_id: str,
    db: Session = Depends(get_db)
):
    """
    Return a single product by product_id.
    """

    product = (
        db.query(Product)
        .filter(
            Product.product_id == product_id
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product_to_dict(product)
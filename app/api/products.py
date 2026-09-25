from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Product


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.get("/")
def get_products(
    limit: int = 20,
    db: Session = Depends(get_db)
):

    limit = min(max(limit, 1), 100)

    products = (
        db.query(Product)
        .limit(limit)
        .all()
    )

    return [
        {
            "product_id": product.product_id,
            "product_name": product.product_name,
            "brand": product.brand,
            "category": product.category,
            "price": product.price,
            "rating": product.rating,
            "quantity_sold": product.quantity_sold,
            "recommendation_score": product.recommendation_score
        }
        for product in products
    ]


@router.get("/{product_id}")
def get_product(
    product_id: str,
    db: Session = Depends(get_db)
):

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

    return {
        "product_id": product.product_id,
        "product_name": product.product_name,
        "brand": product.brand,
        "category": product.category,
        "description": product.description,
        "user_reviews": product.user_reviews,
        "rating": product.rating,
        "price": product.price,
        "quantity_sold": product.quantity_sold,
        "recommendation_score": product.recommendation_score
    }
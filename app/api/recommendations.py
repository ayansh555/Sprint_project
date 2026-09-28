from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User
from app.api.auth import get_current_user
from app.services.recommendation_engine import (
    get_personalized_recommendations,
)

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


@router.get("/")
def recommendations(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    limit = min(max(limit, 1), 50)

    products = get_personalized_recommendations(
        db=db,
        user_id=current_user.user_id,
        limit=limit,
    )

    return {
        "user_id": current_user.user_id,
        "username": current_user.username,
        "recommendations": [
            {
                "product_id": product.product_id,
                "product_name": product.product_name,
                "brand": product.brand,
                "category": product.category,
                "price": product.price,
                "rating": product.rating,
                "recommendation_score": (
                    product.recommendation_score
                ),
                "similarity_score": getattr(
                    product,
                    "similarity_score",
                    0.0,
                ),
                "final_recommendation_score": getattr(
                    product,
                    "final_recommendation_score",
                    0.0,
                ),
                "image_url": product.image_url,
                "product_url": product.product_url,
                "amazon_url": product.amazon_url,
                "flipkart_url": product.flipkart_url,
                "croma_url": product.croma_url,
                "myntra_url": product.myntra_url,
                "reliance_url": product.reliance_url,
                "official_url": product.official_url,
            }
            for product in products
        ],
    }
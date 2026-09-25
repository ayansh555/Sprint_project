from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.services.recommendation_engine import (
    get_personalized_recommendations
)


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)


@router.get("/{user_id}")
def recommendations(
    user_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):

    limit = min(
        max(limit, 1),
        50
    )


    products = (
        get_personalized_recommendations(
            db=db,
            user_id=user_id,
            limit=limit
        )
    )


    return {

        "user_id": user_id,

        "recommendations": [

            {

                "product_id":
                    product.product_id,

                "product_name":
                    product.product_name,

                "brand":
                    product.brand,

                "category":
                    product.category,

                "price":
                    product.price,

                "rating":
                    product.rating,

                "recommendation_score":
                    product.recommendation_score

            }

            for product in products

        ]

    }
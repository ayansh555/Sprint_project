from sqlalchemy import desc

from app.database.models import (
    Product,
    UserInteraction
)


INTERACTION_WEIGHTS = {

    "view": 1.0,

    "click": 2.0,

    "wishlist": 4.0,

    "cart": 6.0,

    "purchase": 10.0
}


def get_user_preferences(
    db,
    user_id: str
):

    interactions = (
        db.query(UserInteraction)
        .filter(
            UserInteraction.user_id == user_id
        )
        .all()
    )


    if not interactions:

        return []


    product_scores = {}


    for interaction in interactions:

        weight = INTERACTION_WEIGHTS.get(
            interaction.interaction_type,
            1.0
        )


        product_id = (
            interaction.product_id
        )


        product_scores[product_id] = (
            product_scores.get(
                product_id,
                0
            ) + weight
        )


    return sorted(
        product_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )


def get_personalized_recommendations(
    db,
    user_id: str,
    limit: int = 10
):

    preferences = get_user_preferences(
        db,
        user_id
    )


    if not preferences:

        return (
            db.query(Product)
            .order_by(
                desc(
                    Product.recommendation_score
                ),
                desc(
                    Product.rating
                )
            )
            .limit(limit)
            .all()
        )


    interacted_product_ids = {

        product_id

        for product_id, score
        in preferences

    }


    recommendations = (
        db.query(Product)

        .filter(
            ~Product.product_id.in_(
                interacted_product_ids
            )
        )

        .order_by(
            desc(
                Product.recommendation_score
            ),

            desc(
                Product.rating
            )
        )

        .limit(limit)

        .all()
    )


    return recommendations
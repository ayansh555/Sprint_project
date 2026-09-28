from uuid import uuid4
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import (
    User,
    Product,
    UserInteraction,
)

from app.api.auth import get_current_user


router = APIRouter(
    prefix="/interactions",
    tags=["User Interactions"]
)


# ============================================================
# RECORD USER INTERACTION
# ============================================================

@router.post("/")
def record_interaction(
    product_id: str,
    interaction_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Record an interaction between the logged-in user
    and a product.
    """

    # --------------------------------------------------------
    # Allowed interaction types
    # --------------------------------------------------------

    allowed_interactions = {
        "view",
        "click",
        "wishlist",
        "cart",
        "purchase",
    }

    if interaction_type not in allowed_interactions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid interaction type. "
                "Allowed values: "
                "view, click, wishlist, cart, purchase"
            ),
        )

    # --------------------------------------------------------
    # Check product
    # --------------------------------------------------------

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
            detail="Product not found",
        )

    # --------------------------------------------------------
    # Create interaction
    # --------------------------------------------------------

    interaction = UserInteraction(
        interaction_id=f"INT-{uuid4().hex[:12]}",
        user_id=current_user.user_id,
        product_id=product.product_id,
        interaction_type=interaction_type,
        timestamp=datetime.now(timezone.utc),
    )

    # --------------------------------------------------------
    # Save interaction
    # --------------------------------------------------------

    db.add(interaction)
    db.commit()
    db.refresh(interaction)

    return {
        "message": "Interaction recorded successfully",
        "interaction_id": interaction.interaction_id,
        "user_id": current_user.user_id,
        "product_id": product.product_id,
        "interaction_type": interaction.interaction_type,
        "timestamp": interaction.timestamp,
    }
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship

from .connection import Base


# ============================================================
# PRODUCT MODEL
# ============================================================

class Product(Base):

    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    product_id = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    product_name = Column(
        String(500)
    )

    brand = Column(
        String(255)
    )

    category = Column(
        String(255)
    )

    description = Column(
        Text
    )

    user_reviews = Column(
        Text
    )

    rating = Column(
        Float
    )

    price = Column(
        Float
    )

    quantity_sold = Column(
        Integer
    )

    search_text = Column(
        Text
    )

    recommendation_score = Column(
        Float
    )

    # --------------------------------------------------------
    # Product Image and Links
    # --------------------------------------------------------

    image_url = Column(
        Text
    )

    product_url = Column(
        Text
    )

    amazon_url = Column(
        Text
    )

    flipkart_url = Column(
        Text
    )

    croma_url = Column(
        Text
    )

    myntra_url = Column(
        Text
    )

    reliance_url = Column(
        Text
    )

    official_url = Column(
        Text
    )

    # --------------------------------------------------------
    # Relationship
    # --------------------------------------------------------

    interactions = relationship(
        "UserInteraction",
        back_populates="product"
    )


# ============================================================
# USER MODEL
# ============================================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    username = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    # --------------------------------------------------------
    # Relationship
    # --------------------------------------------------------

    interactions = relationship(
        "UserInteraction",
        back_populates="user"
    )


# ============================================================
# USER INTERACTION MODEL
# ============================================================

class UserInteraction(Base):

    __tablename__ = "user_interactions"

    id = Column(
        Integer,
        primary_key=True
    )

    interaction_id = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    user_id = Column(
        String(100),
        ForeignKey("users.user_id"),
        nullable=False,
        index=True
    )

    product_id = Column(
        String(100),
        ForeignKey("products.product_id"),
        nullable=False,
        index=True
    )

    interaction_type = Column(
        String(50),
        nullable=False
    )

    timestamp = Column(
        DateTime,
        nullable=False
    )

    # --------------------------------------------------------
    # Relationships
    # --------------------------------------------------------

    user = relationship(
        "User",
        back_populates="interactions"
    )

    product = relationship(
        "Product",
        back_populates="interactions"
    )
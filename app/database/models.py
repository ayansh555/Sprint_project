from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime
)

from .connection import Base


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

    product_name = Column(String(500))

    brand = Column(String(255))

    category = Column(String(255))

    description = Column(Text)

    user_reviews = Column(Text)

    rating = Column(Float)

    price = Column(Float)

    quantity_sold = Column(Integer)

    search_text = Column(Text)

    recommendation_score = Column(Float)


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


class UserInteraction(Base):

    __tablename__ = "user_interactions"

    id = Column(
        Integer,
        primary_key=True
    )

    interaction_id = Column(
        String(100),
        unique=True,
        nullable=False
    )

    user_id = Column(
        String(100),
        nullable=False,
        index=True
    )

    product_id = Column(
        String(100),
        nullable=False,
        index=True
    )

    interaction_type = Column(
        String(50)
    )

    timestamp = Column(
        DateTime
    )
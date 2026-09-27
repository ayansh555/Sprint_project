from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from .env")


engine = create_engine(DATABASE_URL)


with engine.begin() as conn:

    conn.execute(
        text(
            "ALTER TABLE products "
            "ADD COLUMN IF NOT EXISTS image_url TEXT"
        )
    )

    conn.execute(
        text(
            "ALTER TABLE products "
            "ADD COLUMN IF NOT EXISTS product_url TEXT"
        )
    )

    conn.execute(
        text(
            "ALTER TABLE products "
            "ADD COLUMN IF NOT EXISTS amazon_url TEXT"
        )
    )

    conn.execute(
        text(
            "ALTER TABLE products "
            "ADD COLUMN IF NOT EXISTS flipkart_url TEXT"
        )
    )

    conn.execute(
        text(
            "ALTER TABLE products "
            "ADD COLUMN IF NOT EXISTS croma_url TEXT"
        )
    )

    conn.execute(
        text(
            "ALTER TABLE products "
            "ADD COLUMN IF NOT EXISTS reliance_url TEXT"
        )
    )

    conn.execute(
        text(
            "ALTER TABLE products "
            "ADD COLUMN IF NOT EXISTS official_url TEXT"
        )
    )


print("Retailer URL columns added successfully.")
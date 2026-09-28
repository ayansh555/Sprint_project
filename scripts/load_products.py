import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import delete

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.database.connection import SessionLocal
from app.database.models import Product


CSV_FILE = BASE_DIR / "data" / "real_products_10000.csv"


def clean_value(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    if not value or value.lower() == "nan":
        return None

    return value


def load_products():

    print("Loading new 10,000-product dataset...")

    df = pd.read_csv(CSV_FILE)

    print(f"Found {len(df)} products.")

    db = SessionLocal()

    try:

        # -----------------------------------------
        # Delete old product catalog
        # -----------------------------------------

        print("Deleting old products...")

        db.execute(delete(Product))
        db.commit()

        print("Old product catalog deleted.")

        # -----------------------------------------
        # Prepare new products
        # -----------------------------------------

        products = []

        for _, row in df.iterrows():

            product = Product(

                # Basic product information
                product_id=clean_value(row["Product_ID"]),
                product_name=clean_value(row["Product_Name"]),
                brand=clean_value(row["Product_Brand_Name"]),
                category=clean_value(row["Product_Category"]),
                description=clean_value(row["Product_Description"]),
                user_reviews=clean_value(row["User_Reviews"]),

                # Product metrics
                rating=(
                    float(row["Rating"])
                    if pd.notna(row["Rating"])
                    else None
                ),

                price=(
                    float(row["Price_of_Product"])
                    if pd.notna(row["Price_of_Product"])
                    else None
                ),

                quantity_sold=(
                    int(row["Quantity_Sold"])
                    if pd.notna(row["Quantity_Sold"])
                    else 0
                ),

                # Semantic search text
                search_text=clean_value(row["Search_Text"]),

                # Recommendation score
                recommendation_score=(
                    float(row["Recommendation_Score"])
                    if pd.notna(row["Recommendation_Score"])
                    else None
                ),

                # Main product information
                image_url=clean_value(row["Image_URL"]),
                product_url=clean_value(row["Product_URL"]),

                # Retailer URLs
                amazon_url=clean_value(row["amazon_url"]),
                flipkart_url=clean_value(row["flipkart_url"]),
                croma_url=clean_value(row["croma_url"]),
                myntra_url=clean_value(row["myntra_url"]),
                reliance_url=clean_value(row["reliance_url"]),
                official_url=clean_value(row["official_url"]),
            )

            products.append(product)

        # -----------------------------------------
        # Insert in batches
        # -----------------------------------------

        batch_size = 500

        for i in range(0, len(products), batch_size):

            batch = products[i:i + batch_size]

            db.add_all(batch)
            db.commit()

            inserted = min(i + batch_size, len(products))

            print(
                f"Inserted {inserted}/{len(products)} products..."
            )

        # -----------------------------------------
        # Verify
        # -----------------------------------------

        count = db.query(Product).count()

        print()
        print("===================================")
        print("PRODUCT LOADING COMPLETED")
        print("===================================")
        print(f"Products in database: {count}")
        print("===================================")

    except Exception as e:

        db.rollback()

        print()
        print("ERROR while loading products:")
        print(e)

        raise

    finally:

        db.close()


if __name__ == "__main__":
    load_products()
import pandas as pd
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import Product


CSV_FILE = "data/amazon_products_converted.csv"


def clean_text(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    if value == "":
        return None

    return value


def clean_float(value):
    try:
        if pd.isna(value):
            return 0.0
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def clean_int(value):
    try:
        if pd.isna(value):
            return 0
        return int(float(value))
    except (ValueError, TypeError):
        return 0


def load_products():
    print("Reading Amazon product dataset...")

    df = pd.read_csv(
        CSV_FILE,
        keep_default_na=False
    )

    print(f"Products found in CSV: {len(df)}")

    db: Session = SessionLocal()

    inserted = 0
    skipped = 0

    try:

        for _, row in df.iterrows():

            product_id = clean_text(row["Product_ID"])

            if not product_id:
                skipped += 1
                continue

            # Check whether product already exists
            existing_product = (
                db.query(Product)
                .filter(Product.product_id == product_id)
                .first()
            )

            if existing_product:
                skipped += 1
                continue

            product = Product(
                product_id=product_id,

                product_name=clean_text(
                    row["Product_Name"]
                ),

                brand=clean_text(
                    row["Product_Brand_Name"]
                ),

                category=clean_text(
                    row["Product_Category"]
                ),

                description=clean_text(
                    row["Product_Description"]
                ),

                user_reviews=clean_text(
                    row["User_Reviews"]
                ),

                rating=clean_float(
                    row["Rating"]
                ),

                price=clean_float(
                    row["Price_of_Product"]
                ),

                quantity_sold=clean_int(
                    row["Quantity_Sold"]
                ),

                search_text=clean_text(
                    row["Search_Text"]
                ),

                recommendation_score=clean_float(
                    row["Recommendation_Score"]
                ),

                image_url=clean_text(
                    row["Image_URL"]
                ),

                product_url=clean_text(
                    row["Product_URL"]
                )
            )

            db.add(product)
            inserted += 1

            # Commit every 100 products
            if inserted % 100 == 0:
                db.commit()
                print(
                    f"Inserted {inserted} products..."
                )

        db.commit()

        print()
        print("=" * 50)
        print("PRODUCT LOADING COMPLETED")
        print("=" * 50)
        print(f"Inserted : {inserted}")
        print(f"Skipped  : {skipped}")
        print(f"Total CSV: {len(df)}")
        print("=" * 50)

    except Exception as e:

        db.rollback()

        print()
        print("ERROR:")
        print(e)

        raise

    finally:
        db.close()


if __name__ == "__main__":
    load_products()
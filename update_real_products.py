import pandas as pd
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import Product


CSV_FILE = "data/amazon_products_converted.csv"


def clean_text(value):
    """
    Convert a value into clean text.
    Empty values become None.
    """
    if pd.isna(value):
        return None

    value = str(value).strip()

    if value == "":
        return None

    return value


def clean_float(value):
    """
    Convert a value into float.
    Invalid or empty values become 0.0.
    """
    try:
        if pd.isna(value):
            return 0.0

        value = str(value).strip()

        if value == "":
            return 0.0

        return float(value)

    except (ValueError, TypeError):
        return 0.0


def clean_int(value):
    """
    Convert a value into integer.
    Invalid or empty values become 0.
    """
    try:
        if pd.isna(value):
            return 0

        value = str(value).strip()

        if value == "":
            return 0

        return int(float(value))

    except (ValueError, TypeError):
        return 0


def update_products():

    print("=" * 60)
    print("UPDATING AMAZON PRODUCTS")
    print("=" * 60)

    print("\nReading Amazon product dataset...")

    df = pd.read_csv(
        CSV_FILE,
        keep_default_na=False
    )

    print(f"Products found in CSV: {len(df)}")

    db: Session = SessionLocal()

    updated = 0
    not_found = 0
    errors = 0

    try:

        for _, row in df.iterrows():

            product_id = clean_text(
                row.get("Product_ID")
            )

            if not product_id:
                continue

            product = (
                db.query(Product)
                .filter(
                    Product.product_id == product_id
                )
                .first()
            )

            if not product:

                not_found += 1

                continue

            # ------------------------------------------------
            # Update basic product information
            # ------------------------------------------------

            product.product_name = clean_text(
                row.get("Product_Name")
            )

            product.brand = clean_text(
                row.get("Product_Brand_Name")
            )

            product.category = clean_text(
                row.get("Product_Category")
            )

            product.description = clean_text(
                row.get("Product_Description")
            )

            product.user_reviews = clean_text(
                row.get("User_Reviews")
            )

            product.rating = clean_float(
                row.get("Rating")
            )

            product.price = clean_float(
                row.get("Price_of_Product")
            )

            product.quantity_sold = clean_int(
                row.get("Quantity_Sold")
            )

            product.search_text = clean_text(
                row.get("Search_Text")
            )

            product.recommendation_score = clean_float(
                row.get("Recommendation_Score")
            )

            # ------------------------------------------------
            # Update image
            # ------------------------------------------------

            image_url = clean_text(
                row.get("Image_URL")
            )

            if image_url:
                product.image_url = image_url

            # ------------------------------------------------
            # Update Amazon product URL
            # ------------------------------------------------

            product_url = clean_text(
                row.get("Product_URL")
            )

            if product_url:

                product.product_url = product_url

                # Since this dataset comes from Amazon,
                # Product_URL is also the Amazon URL.

                product.amazon_url = product_url

            updated += 1

            # Commit every 100 products

            if updated % 100 == 0:

                db.commit()

                print(
                    f"Updated {updated} products..."
                )

        db.commit()

        print("\n" + "=" * 60)
        print("UPDATE COMPLETED")
        print("=" * 60)

        print(f"Products updated : {updated}")
        print(f"Products not found: {not_found}")
        print(f"Errors            : {errors}")

    except Exception as e:

        db.rollback()

        print("\nERROR:")
        print(e)

        raise

    finally:

        db.close()


if __name__ == "__main__":
    update_products()
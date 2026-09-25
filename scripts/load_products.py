import pandas as pd

from app.database.connection import SessionLocal
from app.database.models import Product


CSV_FILE = "data/products_cleaned.csv"


def load_products():

    print("Loading product dataset...")

    df = pd.read_csv(CSV_FILE)

    print(f"Found {len(df)} products.")

    db = SessionLocal()

    try:

        products = []

        for _, row in df.iterrows():

            product = Product(
                product_id=str(row["Product_ID"]),
                product_name=row.get("Product_Name"),
                brand=row.get("Product_Brand_Name"),
                category=row.get("Product_Category"),
                description=row.get("Product_Description"),
                user_reviews=row.get("User_Reviews"),
                rating=row.get("Rating"),
                price=row.get("Price_of_Product"),
                quantity_sold=row.get("Quantity_Sold"),
                search_text=row.get("Search_Text"),
                recommendation_score=row.get(
                    "Recommendation_Score"
                )
            )

            products.append(product)

        db.add_all(products)
        db.commit()

        print(
            f"Successfully inserted {len(products)} products."
        )

    except Exception as e:

        db.rollback()

        print("ERROR:", e)

        raise

    finally:

        db.close()


if __name__ == "__main__":
    load_products()
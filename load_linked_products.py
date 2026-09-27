import pandas as pd
from pathlib import Path

from app.database.connection import SessionLocal
from app.database.models import Product


# ============================================================
# PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

CSV_FILE = (
    BASE_DIR
    / "data"
    / "products_with_retailer_links.csv"
)


# ============================================================
# LOAD DATASET
# ============================================================

print("\nLoading linked product dataset...")

df = pd.read_csv(CSV_FILE)

print(f"CSV rows: {len(df)}")


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Product_ID",
    "Product_Name",
    "Product_Brand_Name",
    "Product_Category",
    "Product_Description",
    "User_Reviews",
    "Rating",
    "Price_of_Product",
    "Quantity_Sold",
    "amazon_search_url",
    "flipkart_url",
    "croma_url",
    "myntra_url",
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing columns: {missing_columns}"
    )

print("All required columns found.")


# ============================================================
# DATABASE
# ============================================================

db = SessionLocal()

updated = 0
inserted = 0
not_found = 0


try:

    print("\nProcessing products...\n")

    for _, row in df.iterrows():

        product_id = str(
            row["Product_ID"]
        ).strip()

        # ----------------------------------------------------
        # FIND EXISTING PRODUCT
        # ----------------------------------------------------

        product = (
            db.query(Product)
            .filter(
                Product.product_id == product_id
            )
            .first()
        )

        # ----------------------------------------------------
        # UPDATE EXISTING PRODUCT
        # ----------------------------------------------------

        if product:

            product.product_name = (
                str(row["Product_Name"])
                if pd.notna(row["Product_Name"])
                else None
            )

            product.brand = (
                str(row["Product_Brand_Name"])
                if pd.notna(row["Product_Brand_Name"])
                else None
            )

            product.category = (
                str(row["Product_Category"])
                if pd.notna(row["Product_Category"])
                else None
            )

            product.description = (
                str(row["Product_Description"])
                if pd.notna(row["Product_Description"])
                else None
            )

            product.user_reviews = (
                str(row["User_Reviews"])
                if pd.notna(row["User_Reviews"])
                else None
            )

            product.rating = (
                float(row["Rating"])
                if pd.notna(row["Rating"])
                else None
            )

            product.price = (
                float(row["Price_of_Product"])
                if pd.notna(row["Price_of_Product"])
                else None
            )

            product.quantity_sold = (
                int(row["Quantity_Sold"])
                if pd.notna(row["Quantity_Sold"])
                else None
            )

            # ------------------------------------------------
            # RETAILER LINKS
            # ------------------------------------------------

            product.amazon_url = (
                str(row["amazon_search_url"])
                if pd.notna(row["amazon_search_url"])
                else None
            )

            product.flipkart_url = (
                str(row["flipkart_url"])
                if pd.notna(row["flipkart_url"])
                else None
            )

            product.croma_url = (
                str(row["croma_url"])
                if pd.notna(row["croma_url"])
                else None
            )

            product.myntra_url = (
                str(row["myntra_url"])
                if pd.notna(row["myntra_url"])
                else None
            )

            updated += 1

        # ----------------------------------------------------
        # PRODUCT DOES NOT EXIST
        # ----------------------------------------------------

        else:

            not_found += 1


    # ========================================================
    # COMMIT
    # ========================================================

    db.commit()

    print("\n")
    print("=" * 65)
    print("LINKED PRODUCT DATASET PROCESSED")
    print("=" * 65)

    print(f"CSV products       : {len(df)}")
    print(f"Products updated   : {updated}")
    print(f"Products not found : {not_found}")
    print(f"Products inserted  : {inserted}")

    print("=" * 65)


except Exception as e:

    db.rollback()

    print("\nERROR:")
    print(e)

    raise


finally:

    db.close()
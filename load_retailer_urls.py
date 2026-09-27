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
    / "amazon_products_with_retailers.csv"
)


# ============================================================
# LOAD CSV
# ============================================================

print("\nLoading retailer dataset...")

df = pd.read_csv(CSV_FILE)

print(f"Total rows found: {len(df)}")


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Product_ID",
    "Product_URL",
    "flipkart_url",
    "croma_url",
    "myntra_url"
]

for column in required_columns:

    if column not in df.columns:
        raise ValueError(
            f"Required column missing from CSV: {column}"
        )


print("\nRequired columns verified.")


# ============================================================
# DATABASE SESSION
# ============================================================

db = SessionLocal()


try:

    updated_count = 0
    not_found_count = 0

    print("\nUpdating products...\n")

    for _, row in df.iterrows():

        product_id = str(row["Product_ID"]).strip()

        product = (
            db.query(Product)
            .filter(
                Product.product_id == product_id
            )
            .first()
        )

        if product is None:

            not_found_count += 1

            continue


        # ----------------------------------------------------
        # Amazon
        # ----------------------------------------------------

        if pd.notna(row["Product_URL"]):

            product.product_url = str(
                row["Product_URL"]
            ).strip()

            product.amazon_url = str(
                row["Product_URL"]
            ).strip()


        # ----------------------------------------------------
        # Flipkart
        # ----------------------------------------------------

        if pd.notna(row["flipkart_url"]):

            product.flipkart_url = str(
                row["flipkart_url"]
            ).strip()


        # ----------------------------------------------------
        # Croma
        # ----------------------------------------------------

        if pd.notna(row["croma_url"]):

            product.croma_url = str(
                row["croma_url"]
            ).strip()


        # ----------------------------------------------------
        # Myntra
        # ----------------------------------------------------

        if pd.notna(row["myntra_url"]):

            product.myntra_url = str(
                row["myntra_url"]
            ).strip()


        updated_count += 1


    # ========================================================
    # COMMIT
    # ========================================================

    db.commit()


    print("\n")
    print("=" * 60)
    print("RETAILER URL UPDATE COMPLETED")
    print("=" * 60)

    print(f"CSV products       : {len(df)}")
    print(f"Products updated   : {updated_count}")
    print(f"Products not found : {not_found_count}")

    print("=" * 60)


except Exception as e:

    db.rollback()

    print("\nERROR:")
    print(e)

    raise


finally:

    db.close()
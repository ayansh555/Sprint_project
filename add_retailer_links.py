import pandas as pd
from urllib.parse import quote_plus
from pathlib import Path


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "amazon_products_converted.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "amazon_products_with_retailers.csv"
)


# =========================================================
# LOAD DATASET
# =========================================================

print("\nLoading Amazon dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Total products loaded: {len(df)}")


# =========================================================
# VERIFY REQUIRED COLUMNS
# =========================================================

required_columns = [
    "Product_ID",
    "Product_Name",
    "Product_URL",
    "Image_URL"
]


for column in required_columns:

    if column not in df.columns:

        raise ValueError(
            f"Required column not found: {column}"
        )


print("\nRequired columns verified.")

print("Amazon URL column : Product_URL")
print("Image column      : Image_URL")
print("Product column    : Product_Name")


# =========================================================
# CLEAN PRODUCT NAMES
# =========================================================

df["Product_Name"] = (
    df["Product_Name"]
    .fillna("")
    .astype(str)
    .str.strip()
)


# =========================================================
# FLIPKART
# =========================================================

def create_flipkart_url(product_name):

    if not product_name:

        return None

    query = quote_plus(product_name)

    return (
        "https://www.flipkart.com/search"
        f"?q={query}"
    )


# =========================================================
# CROMA
# =========================================================

def create_croma_url(product_name):

    if not product_name:

        return None

    query = quote_plus(product_name)

    return (
        "https://www.croma.com/search"
        f"?text={query}"
    )


# =========================================================
# MYNTRA
# =========================================================

def create_myntra_url(product_name):

    if not product_name:

        return None

    query = quote_plus(product_name)

    return (
        "https://www.myntra.com/search"
        f"?rawQuery={query}"
    )


# =========================================================
# CREATE RETAILER LINKS
# =========================================================

print("\nCreating Flipkart links...")

df["flipkart_url"] = (
    df["Product_Name"]
    .apply(create_flipkart_url)
)


print("Creating Croma links...")

df["croma_url"] = (
    df["Product_Name"]
    .apply(create_croma_url)
)


print("Creating Myntra links...")

df["myntra_url"] = (
    df["Product_Name"]
    .apply(create_myntra_url)
)


# =========================================================
# VERIFY AMAZON LINKS
# =========================================================

amazon_count = (
    df["Product_URL"]
    .notna()
    .sum()
)


image_count = (
    df["Image_URL"]
    .notna()
    .sum()
)


print("\nExisting Amazon data:")

print(
    f"Amazon product URLs : {amazon_count}"
)

print(
    f"Product images      : {image_count}"
)


# =========================================================
# SAVE
# =========================================================

print("\nSaving dataset...")

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# =========================================================
# FINAL SUMMARY
# =========================================================

print("\n")
print("=" * 65)

print(
    "RETAILER DATASET CREATED SUCCESSFULLY"
)

print("=" * 65)

print(
    f"Total products      : {len(df)}"
)

print(
    f"Amazon URLs         : "
    f"{df['Product_URL'].notna().sum()}"
)

print(
    f"Flipkart URLs       : "
    f"{df['flipkart_url'].notna().sum()}"
)

print(
    f"Croma URLs          : "
    f"{df['croma_url'].notna().sum()}"
)

print(
    f"Myntra URLs         : "
    f"{df['myntra_url'].notna().sum()}"
)


# =========================================================
# SHOW SAMPLE
# =========================================================

print("\nSample products:\n")


sample_columns = [
    "Product_ID",
    "Product_Name",
    "Product_URL",
    "flipkart_url",
    "croma_url",
    "myntra_url"
]


print(
    df[
        sample_columns
    ]
    .head(5)
    .to_string(index=False)
)


# =========================================================
# OUTPUT
# =========================================================

print("\n")
print("Output file:")

print(OUTPUT_FILE)

print("\nDone.")
import pandas as pd
import numpy as np

from pathlib import Path
from sentence_transformers import SentenceTransformer


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ORIGINAL_DATA_FILE = (
    BASE_DIR
    / "data"
    / "products_cleaned.csv"
)

REAL_PRODUCTS_FILE = (
    BASE_DIR
    / "data"
    / "amazon_products_converted.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "embeddings"
)

OUTPUT_DIR.mkdir(
    exist_ok=True
)


# ============================================================
# EMBEDDING MODEL
# ============================================================

MODEL_NAME = "all-MiniLM-L6-v2"


# ============================================================
# LOAD ORIGINAL PRODUCTS
# ============================================================

print()
print("=" * 60)
print("LOADING ORIGINAL PRODUCTS")
print("=" * 60)

original_df = pd.read_csv(
    ORIGINAL_DATA_FILE,
    keep_default_na=False
)

print(
    f"Original products: {len(original_df)}"
)


# ============================================================
# LOAD REAL AMAZON PRODUCTS
# ============================================================

print()
print("=" * 60)
print("LOADING REAL AMAZON PRODUCTS")
print("=" * 60)

real_df = pd.read_csv(
    REAL_PRODUCTS_FILE,
    keep_default_na=False
)

print(
    f"Real Amazon products: {len(real_df)}"
)


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Product_ID",
    "Search_Text"
]

for column in required_columns:

    if column not in original_df.columns:
        raise ValueError(
            f"Missing column '{column}' "
            f"in products_cleaned.csv"
        )

    if column not in real_df.columns:
        raise ValueError(
            f"Missing column '{column}' "
            f"in amazon_products_converted.csv"
        )


# ============================================================
# COMBINE DATASETS
# ============================================================

print()
print("=" * 60)
print("COMBINING PRODUCTS")
print("=" * 60)

combined_df = pd.concat(
    [
        original_df,
        real_df
    ],
    ignore_index=True
)


# ============================================================
# CHECK DUPLICATE PRODUCT IDs
# ============================================================

duplicate_count = (
    combined_df["Product_ID"]
    .astype(str)
    .duplicated()
    .sum()
)

if duplicate_count > 0:

    print(
        f"WARNING: {duplicate_count} duplicate "
        f"Product_ID values found."
    )

    combined_df = (
        combined_df
        .drop_duplicates(
            subset=["Product_ID"],
            keep="first"
        )
        .reset_index(drop=True)
    )


print(
    f"Total products for embeddings: "
    f"{len(combined_df)}"
)


# ============================================================
# PREPARE SEARCH TEXT
# ============================================================

texts = (
    combined_df["Search_Text"]
    .fillna("")
    .astype(str)
    .tolist()
)


# ============================================================
# LOAD SENTENCE TRANSFORMER
# ============================================================

print()
print("=" * 60)
print("LOADING EMBEDDING MODEL")
print("=" * 60)

print(
    f"Model: {MODEL_NAME}"
)

model = SentenceTransformer(
    MODEL_NAME
)


# ============================================================
# GENERATE EMBEDDINGS
# ============================================================

print()
print("=" * 60)
print("GENERATING EMBEDDINGS")
print("=" * 60)

print(
    f"Generating embeddings for "
    f"{len(texts)} products..."
)

embeddings = model.encode(
    texts,
    batch_size=32,
    show_progress_bar=True,
    normalize_embeddings=True
)

embeddings = np.asarray(
    embeddings,
    dtype=np.float32
)


# ============================================================
# SAVE EMBEDDINGS
# ============================================================

np.save(
    OUTPUT_DIR / "product_embeddings.npy",
    embeddings
)


# ============================================================
# SAVE PRODUCT IDs
# ============================================================

product_ids = (
    combined_df["Product_ID"]
    .astype(str)
    .to_numpy()
)

np.save(
    OUTPUT_DIR / "product_ids.npy",
    product_ids
)


# ============================================================
# FINAL INFORMATION
# ============================================================

print()
print("=" * 60)
print("EMBEDDING GENERATION COMPLETED")
print("=" * 60)

print(
    "Total products:",
    len(combined_df)
)

print(
    "Embedding shape:",
    embeddings.shape
)

print(
    "Product IDs:",
    len(product_ids)
)

print()
print(
    "Embeddings saved to:"
)

print(
    OUTPUT_DIR / "product_embeddings.npy"
)

print()
print(
    "Product IDs saved to:"
)

print(
    OUTPUT_DIR / "product_ids.npy"
)

print()
print("=" * 60)
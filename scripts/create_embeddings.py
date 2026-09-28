import pandas as pd
import numpy as np

from pathlib import Path
from sentence_transformers import SentenceTransformer


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PRODUCTS_FILE = (
    BASE_DIR
    / "data"
    / "real_products_10000.csv"
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
# LOAD NEW 10K PRODUCT DATASET
# ============================================================

print()
print("=" * 60)
print("LOADING 10K PRODUCT DATASET")
print("=" * 60)

df = pd.read_csv(
    PRODUCTS_FILE,
    keep_default_na=False
)

print(
    f"Products loaded: {len(df)}"
)


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Product_ID",
    "Search_Text"
]

for column in required_columns:

    if column not in df.columns:

        raise ValueError(
            f"Missing required column: {column}"
        )


# ============================================================
# REMOVE DUPLICATE PRODUCT IDs
# ============================================================

duplicate_count = (
    df["Product_ID"]
    .astype(str)
    .duplicated()
    .sum()
)

if duplicate_count > 0:

    print(
        f"Removing {duplicate_count} duplicate Product_IDs..."
    )

    df = (
        df
        .drop_duplicates(
            subset=["Product_ID"],
            keep="first"
        )
        .reset_index(drop=True)
    )


print(
    f"Products for embeddings: {len(df)}"
)


# ============================================================
# PREPARE SEARCH TEXT
# ============================================================

texts = (
    df["Search_Text"]
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

embedding_file = (
    OUTPUT_DIR
    / "product_embeddings.npy"
)

np.save(
    embedding_file,
    embeddings
)


# ============================================================
# SAVE PRODUCT IDs
# ============================================================

product_ids = (
    df["Product_ID"]
    .astype(str)
    .to_numpy()
)

product_ids_file = (
    OUTPUT_DIR
    / "product_ids.npy"
)

np.save(
    product_ids_file,
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
    len(df)
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
print("Embeddings saved to:")
print(embedding_file)

print()
print("Product IDs saved to:")
print(product_ids_file)

print()
print("=" * 60)
import pandas as pd
import numpy as np

from pathlib import Path
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    BASE_DIR
    / "data"
    / "products_cleaned.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "embeddings"
)

OUTPUT_DIR.mkdir(
    exist_ok=True
)


MODEL_NAME = "all-MiniLM-L6-v2"


print("Loading product dataset...")

df = pd.read_csv(DATA_FILE)

texts = (
    df["Search_Text"]
    .fillna("")
    .astype(str)
    .tolist()
)


print(
    f"Generating embeddings for "
    f"{len(texts)} products..."
)

model = SentenceTransformer(
    MODEL_NAME
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


np.save(
    OUTPUT_DIR
    / "product_embeddings.npy",
    embeddings
)

np.save(
    OUTPUT_DIR
    / "product_ids.npy",
    df["Product_ID"]
    .astype(str)
    .to_numpy()
)


print(
    "Embedding shape:",
    embeddings.shape
)

print(
    "Embeddings saved successfully."
)
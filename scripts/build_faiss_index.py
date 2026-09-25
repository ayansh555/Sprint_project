import faiss
import numpy as np

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

EMBEDDING_FILE = (
    BASE_DIR
    / "embeddings"
    / "product_embeddings.npy"
)

INDEX_FILE = (
    BASE_DIR
    / "embeddings"
    / "products.index"
)


print("Loading embeddings...")

embeddings = np.load(
    EMBEDDING_FILE
)

print(
    "Embedding shape:",
    embeddings.shape
)


dimension = embeddings.shape[1]


index = faiss.IndexFlatIP(
    dimension
)

index.add(embeddings)


faiss.write_index(
    index,
    str(INDEX_FILE)
)


print(
    f"FAISS index created with "
    f"{index.ntotal} products."
)
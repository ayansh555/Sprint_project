import faiss
import numpy as np

from pathlib import Path

from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent.parent.parent

INDEX_FILE = (
    BASE_DIR
    / "embeddings"
    / "products.index"
)

PRODUCT_IDS_FILE = (
    BASE_DIR
    / "embeddings"
    / "product_ids.npy"
)


MODEL_NAME = "all-MiniLM-L6-v2"


class SemanticSearch:

    def __init__(self):

        self.model = SentenceTransformer(
            MODEL_NAME
        )

        self.index = faiss.read_index(
            str(INDEX_FILE)
        )

        self.product_ids = np.load(
            PRODUCT_IDS_FILE,
            allow_pickle=True
        )

    def search(
        self,
        query: str,
        top_k: int = 5
    ):

        query_embedding = (
            self.model.encode(
                [query],
                normalize_embeddings=True
            )
        )

        scores, indices = (
            self.index.search(
                query_embedding,
                top_k
            )
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            results.append(
                {
                    "product_id": str(
                        self.product_ids[index]
                    ),
                    "similarity_score": float(
                        score
                    )
                }
            )

        return results
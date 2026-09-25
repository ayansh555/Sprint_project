import os

import numpy as np

from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer


load_dotenv()


MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2"
)


class EmbeddingService:

    def __init__(self):

        print(
            f"Loading embedding model: {MODEL_NAME}"
        )

        self.model = SentenceTransformer(
            MODEL_NAME
        )

        print(
            "Embedding model loaded successfully."
        )


    def encode_text(
        self,
        text: str
    ):

        embedding = self.model.encode(
            [text],
            normalize_embeddings=True
        )

        return np.asarray(
            embedding[0],
            dtype=np.float32
        )


    def encode_texts(
        self,
        texts
    ):

        embeddings = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=True,
            normalize_embeddings=True
        )

        return np.asarray(
            embeddings,
            dtype=np.float32
        )
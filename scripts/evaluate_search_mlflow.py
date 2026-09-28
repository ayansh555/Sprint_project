import os
import time
import math
import random

import faiss
import mlflow
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATASET_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "real_products_10000.csv"
)

EVALUATION_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "evaluation_queries.csv"
)

EMBEDDINGS_PATH = os.path.join(
    PROJECT_ROOT,
    "embeddings",
    "product_embeddings.npy"
)

PRODUCT_IDS_PATH = os.path.join(
    PROJECT_ROOT,
    "embeddings",
    "product_ids.npy"
)

FAISS_INDEX_PATH = os.path.join(
    PROJECT_ROOT,
    "embeddings",
    "products.index"
)


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2"
)

TOP_K_VALUES = [1, 5, 10]

NUMBER_OF_EVALUATION_QUERIES = 100

RANDOM_SEED = 42

EXPERIMENT_NAME = (
    "AI-ECommerce-Search-Recommendation"
)


# ============================================================
# LOAD DATASET
# ============================================================

print("\nLoading dataset...")

df = pd.read_csv(DATASET_PATH)

print(
    f"Dataset loaded: {len(df)} products"
)


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Product_ID",
    "Product_Name",
    "Product_Brand_Name",
    "Product_Category",
    "Product_Description",
    "Search_Text",
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


# ============================================================
# CREATE EVALUATION DATASET
# ============================================================

if not os.path.exists(EVALUATION_PATH):

    print(
        "\nEvaluation dataset not found."
    )

    print(
        "Creating evaluation_queries.csv..."
    )

    random.seed(RANDOM_SEED)

    evaluation_df = df[
        [
            "Product_ID",
            "Product_Name",
            "Product_Brand_Name",
            "Product_Category",
        ]
    ].dropna(
        subset=["Product_ID", "Product_Name"]
    )

    sample_size = min(
        NUMBER_OF_EVALUATION_QUERIES,
        len(evaluation_df)
    )

    evaluation_df = evaluation_df.sample(
        n=sample_size,
        random_state=RANDOM_SEED
    )

    rows = []

    for _, row in evaluation_df.iterrows():

        product_id = str(
            row["Product_ID"]
        )

        product_name = str(
            row["Product_Name"]
        )

        brand = str(
            row["Product_Brand_Name"]
        ) if pd.notna(
            row["Product_Brand_Name"]
        ) else ""

        category = str(
            row["Product_Category"]
        ) if pd.notna(
            row["Product_Category"]
        ) else ""

        query_parts = []

        if brand:
            query_parts.append(brand)

        if category:
            query_parts.append(category)

        query_parts.append(product_name)

        query = " ".join(
            query_parts
        ).strip()

        rows.append(
            {
                "query": query,
                "relevant_product_id": product_id,
            }
        )

    evaluation_data = pd.DataFrame(
        rows
    )

    evaluation_data.to_csv(
        EVALUATION_PATH,
        index=False
    )

    print(
        f"Created {EVALUATION_PATH}"
    )

else:

    print(
        "\nUsing existing evaluation dataset:"
    )

    print(EVALUATION_PATH)


# ============================================================
# LOAD EVALUATION DATA
# ============================================================

evaluation_data = pd.read_csv(
    EVALUATION_PATH
)

print(
    f"Evaluation queries: "
    f"{len(evaluation_data)}"
)


# ============================================================
# LOAD MODEL
# ============================================================

print(
    "\nLoading SentenceTransformer model..."
)

model = SentenceTransformer(
    MODEL_NAME
)

print(
    f"Model loaded: {MODEL_NAME}"
)


# ============================================================
# LOAD FAISS
# ============================================================

print(
    "\nLoading FAISS index..."
)

index = faiss.read_index(
    FAISS_INDEX_PATH
)

print(
    f"FAISS index loaded."
)

print(
    f"FAISS vectors: {index.ntotal}"
)


# ============================================================
# LOAD PRODUCT IDS
# ============================================================

product_ids = np.load(
    PRODUCT_IDS_PATH,
    allow_pickle=True
)

product_ids = [
    str(product_id)
    for product_id in product_ids
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def precision_at_k(
    retrieved_ids,
    relevant_id,
    k
):

    retrieved = retrieved_ids[:k]

    relevant_count = sum(
        1
        for product_id in retrieved
        if product_id == relevant_id
    )

    return relevant_count / k


def recall_at_k(
    retrieved_ids,
    relevant_id,
    k
):

    retrieved = retrieved_ids[:k]

    if relevant_id in retrieved:
        return 1.0

    return 0.0


def reciprocal_rank(
    retrieved_ids,
    relevant_id
):

    for position, product_id in enumerate(
        retrieved_ids,
        start=1
    ):

        if product_id == relevant_id:

            return 1.0 / position

    return 0.0


def ndcg_at_k(
    retrieved_ids,
    relevant_id,
    k
):

    retrieved = retrieved_ids[:k]

    for position, product_id in enumerate(
        retrieved,
        start=1
    ):

        if product_id == relevant_id:

            return 1.0 / math.log2(
                position + 1
            )

    return 0.0


# ============================================================
# RUN EVALUATION
# ============================================================

print(
    "\nStarting evaluation..."
)

results = []

latencies = []

for index_number, row in evaluation_data.iterrows():

    query = str(
        row["query"]
    )

    relevant_id = str(
        row["relevant_product_id"]
    )

    # ----------------------------------------
    # Encode query
    # ----------------------------------------

    start_time = time.perf_counter()

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    ).astype(np.float32)

    # ----------------------------------------
    # FAISS search
    # ----------------------------------------

    distances, indices = index.search(
        query_embedding,
        max(TOP_K_VALUES)
    )

    latency_ms = (
        time.perf_counter()
        - start_time
    ) * 1000

    latencies.append(
        latency_ms
    )

    retrieved_ids = []

    for vector_index in indices[0]:

        if vector_index < 0:
            continue

        if vector_index >= len(product_ids):
            continue

        retrieved_ids.append(
            product_ids[vector_index]
        )

    result = {
        "query": query,
        "relevant_product_id": relevant_id,
        "retrieved_product_ids": retrieved_ids,
        "latency_ms": latency_ms,
    }

    # ----------------------------------------
    # Metrics
    # ----------------------------------------

    for k in TOP_K_VALUES:

        result[
            f"precision_at_{k}"
        ] = precision_at_k(
            retrieved_ids,
            relevant_id,
            k
        )

        result[
            f"recall_at_{k}"
        ] = recall_at_k(
            retrieved_ids,
            relevant_id,
            k
        )

        result[
            f"ndcg_at_{k}"
        ] = ndcg_at_k(
            retrieved_ids,
            relevant_id,
            k
        )

    result["reciprocal_rank"] = reciprocal_rank(
        retrieved_ids,
        relevant_id
    )

    results.append(
        result
    )

    if (index_number + 1) % 10 == 0:

        print(
            f"Evaluated "
            f"{index_number + 1}/"
            f"{len(evaluation_data)} queries"
        )


# ============================================================
# CONVERT RESULTS TO DATAFRAME
# ============================================================

results_df = pd.DataFrame(
    results
)


# ============================================================
# CALCULATE FINAL METRICS
# ============================================================

metrics = {}


for k in TOP_K_VALUES:

    metrics[
        f"precision_at_{k}"
    ] = float(
        results_df[
            f"precision_at_{k}"
        ].mean()
    )

    metrics[
        f"recall_at_{k}"
    ] = float(
        results_df[
            f"recall_at_{k}"
        ].mean()
    )

    metrics[
        f"ndcg_at_{k}"
    ] = float(
        results_df[
            f"ndcg_at_{k}"
        ].mean()
    )


metrics["mrr"] = float(
    results_df[
        "reciprocal_rank"
    ].mean()
)

metrics["average_search_latency_ms"] = float(
    np.mean(latencies)
)

metrics["p95_search_latency_ms"] = float(
    np.percentile(
        latencies,
        95
    )
)


# ============================================================
# PRINT RESULTS
# ============================================================

print("\n")
print("=" * 60)
print("SEARCH EVALUATION RESULTS")
print("=" * 60)

for metric_name, value in metrics.items():

    print(
        f"{metric_name}: {value:.4f}"
    )

print("=" * 60)


# ============================================================
# SAVE LOCAL RESULTS
# ============================================================

results_path = os.path.join(
    PROJECT_ROOT,
    "data",
    "search_evaluation_results.csv"
)

results_df.to_csv(
    results_path,
    index=False
)

print(
    f"\nResults saved to:"
    f"\n{results_path}"
)


# ============================================================
# MLFLOW
# ============================================================

print(
    "\nLogging results to MLflow..."
)

mlflow.set_experiment(
    EXPERIMENT_NAME
)


with mlflow.start_run(
    run_name="semantic-search-evaluation"
):

    # ----------------------------------------
    # Parameters
    # ----------------------------------------

    mlflow.log_param(
        "model_name",
        MODEL_NAME
    )

    mlflow.log_param(
        "model_type",
        "Sentence Transformer"
    )

    mlflow.log_param(
        "embedding_dimension",
        384
    )

    mlflow.log_param(
        "dataset",
        "real_products_10000.csv"
    )

    mlflow.log_param(
        "product_count",
        len(df)
    )

    mlflow.log_param(
        "evaluation_queries",
        len(evaluation_data)
    )

    mlflow.log_param(
        "faiss_index_type",
        "IndexFlatIP"
    )

    mlflow.log_param(
        "top_k_values",
        str(TOP_K_VALUES)
    )

    # ----------------------------------------
    # Metrics
    # ----------------------------------------

    for metric_name, value in metrics.items():

        mlflow.log_metric(
            metric_name,
            value
        )

    # ----------------------------------------
    # Artifacts
    # ----------------------------------------

    mlflow.log_artifact(
        EVALUATION_PATH,
        artifact_path="evaluation"
    )

    mlflow.log_artifact(
        results_path,
        artifact_path="evaluation"
    )

    mlflow.log_artifact(
        DATASET_PATH,
        artifact_path="dataset"
    )

    if os.path.exists(
        EMBEDDINGS_PATH
    ):

        mlflow.log_artifact(
            EMBEDDINGS_PATH,
            artifact_path="embeddings"
        )

    if os.path.exists(
        PRODUCT_IDS_PATH
    ):

        mlflow.log_artifact(
            PRODUCT_IDS_PATH,
            artifact_path="embeddings"
        )

    if os.path.exists(
        FAISS_INDEX_PATH
    ):

        mlflow.log_artifact(
            FAISS_INDEX_PATH,
            artifact_path="faiss"
        )

    print(
        "\nMLflow evaluation run completed."
    )
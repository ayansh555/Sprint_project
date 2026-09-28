import os
import mlflow


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


EXPERIMENT_NAME = "AI-ECommerce-Search-Recommendation"


mlflow.set_experiment(EXPERIMENT_NAME)


with mlflow.start_run(
    run_name="semantic-search-artifacts"
):

    # ==========================================
    # PARAMETERS
    # ==========================================

    mlflow.log_param(
        "embedding_model",
        os.getenv(
            "EMBEDDING_MODEL",
            "all-MiniLM-L6-v2"
        )
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
        10000
    )

    mlflow.log_param(
        "faiss_index",
        "IndexFlatIP"
    )

    mlflow.log_param(
        "similarity_method",
        "Inner Product / Cosine Similarity"
    )

    # ==========================================
    # CONFIGURATION ARTIFACT
    # ==========================================

    config_path = os.path.join(
        PROJECT_ROOT,
        "mlflow_config.txt"
    )

    with open(config_path, "w") as f:

        f.write(
            "AI E-Commerce Search & Recommendation System\n"
        )
        f.write(
            "============================================\n"
        )
        f.write(
            "Dataset: real_products_10000.csv\n"
        )
        f.write(
            "Product Count: 10000\n"
        )
        f.write(
            "Embedding Model: all-MiniLM-L6-v2\n"
        )
        f.write(
            "Embedding Dimension: 384\n"
        )
        f.write(
            "FAISS Index: IndexFlatIP\n"
        )
        f.write(
            "Similarity: Inner Product / Cosine Similarity\n"
        )

    mlflow.log_artifact(
        config_path,
        artifact_path="configuration"
    )

    # ==========================================
    # DATASET ARTIFACT
    # ==========================================

    dataset_path = os.path.join(
        PROJECT_ROOT,
        "data",
        "real_products_10000.csv"
    )

    if os.path.exists(dataset_path):

        mlflow.log_artifact(
            dataset_path,
            artifact_path="dataset"
        )

        print(
            "Dataset artifact logged:"
            " real_products_10000.csv"
        )

    else:

        print(
            "Dataset not found:",
            dataset_path
        )

    # ==========================================
    # EMBEDDINGS ARTIFACT
    # ==========================================

    embeddings_path = os.path.join(
        PROJECT_ROOT,
        "embeddings",
        "product_embeddings.npy"
    )

    if os.path.exists(embeddings_path):

        mlflow.log_artifact(
            embeddings_path,
            artifact_path="embeddings"
        )

        print(
            "Embedding artifact logged."
        )

    else:

        print(
            "Embeddings file not found."
        )

    # ==========================================
    # PRODUCT IDS ARTIFACT
    # ==========================================

    product_ids_path = os.path.join(
        PROJECT_ROOT,
        "embeddings",
        "product_ids.npy"
    )

    if os.path.exists(product_ids_path):

        mlflow.log_artifact(
            product_ids_path,
            artifact_path="embeddings"
        )

        print(
            "Product IDs artifact logged."
        )

    else:

        print(
            "Product IDs file not found."
        )

    # ==========================================
    # FAISS ARTIFACT
    # ==========================================

    faiss_path = os.path.join(
        PROJECT_ROOT,
        "embeddings",
        "products.index"
    )

    if os.path.exists(faiss_path):

        mlflow.log_artifact(
            faiss_path,
            artifact_path="faiss"
        )

        print(
            "FAISS index artifact logged."
        )

    else:

        print(
            "FAISS index not found."
        )

    # ==========================================
    # REQUIREMENTS ARTIFACT
    # ==========================================

    requirements_path = os.path.join(
        PROJECT_ROOT,
        "requirements.txt"
    )

    if os.path.exists(requirements_path):

        mlflow.log_artifact(
            requirements_path,
            artifact_path="environment"
        )

        print(
            "Requirements artifact logged."
        )

    else:

        print(
            "requirements.txt not found."
        )


print()
print(
    "MLflow artifacts logged successfully." 
)
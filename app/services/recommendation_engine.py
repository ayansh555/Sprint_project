import os
import math
from functools import lru_cache
from datetime import datetime, timezone

import faiss
import numpy as np

from sqlalchemy import desc

from sentence_transformers import SentenceTransformer

from app.database.models import (
    Product,
    UserInteraction,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2",
)


FAISS_INDEX_PATH = os.path.join(
    BASE_DIR,
    "embeddings",
    "products.index",
)


PRODUCT_IDS_PATH = os.path.join(
    BASE_DIR,
    "embeddings",
    "product_ids.npy",
)


# ============================================================
# INTERACTION WEIGHTS
# ============================================================

INTERACTION_WEIGHTS = {
    "view": 1.0,
    "click": 2.5,
    "wishlist": 5.0,
    "cart": 7.0,
    "purchase": 10.0,
}


# Recent interactions receive more importance.
# Half-life is approximately 14 days.
RECENCY_HALF_LIFE_DAYS = 14.0


# ============================================================
# RECOMMENDATION SETTINGS
# ============================================================

DEFAULT_LIMIT = 10

MAX_LIMIT = 50

FAISS_CANDIDATE_MULTIPLIER = 20

MIN_FAISS_CANDIDATES = 100

MAX_FAISS_CANDIDATES = 500


# ============================================================
# CACHED MODEL
# ============================================================

@lru_cache(maxsize=1)
def get_embedding_model():

    print(
        f"Loading embedding model: "
        f"{EMBEDDING_MODEL_NAME}"
    )

    return SentenceTransformer(
        EMBEDDING_MODEL_NAME
    )


# ============================================================
# CACHED FAISS INDEX
# ============================================================

@lru_cache(maxsize=1)
def get_faiss_index():

    if not os.path.exists(
        FAISS_INDEX_PATH
    ):

        raise FileNotFoundError(
            f"FAISS index not found: "
            f"{FAISS_INDEX_PATH}"
        )

    print(
        f"Loading FAISS index: "
        f"{FAISS_INDEX_PATH}"
    )

    return faiss.read_index(
        FAISS_INDEX_PATH
    )


# ============================================================
# CACHED PRODUCT IDS
# ============================================================

@lru_cache(maxsize=1)
def get_faiss_product_ids():

    if not os.path.exists(
        PRODUCT_IDS_PATH
    ):

        raise FileNotFoundError(
            f"Product ID file not found: "
            f"{PRODUCT_IDS_PATH}"
        )

    product_ids = np.load(
        PRODUCT_IDS_PATH,
        allow_pickle=True,
    )

    return [
        str(product_id)
        for product_id in product_ids
    ]


# ============================================================
# NORMALIZE VECTOR
# ============================================================

def normalize_vector(vector):

    vector = np.asarray(
        vector,
        dtype=np.float32,
    )

    norm = np.linalg.norm(
        vector
    )

    if norm == 0:

        return vector

    return vector / norm


# ============================================================
# RECENCY WEIGHT
# ============================================================

def calculate_recency_weight(timestamp):

    if timestamp is None:

        return 1.0

    try:

        if timestamp.tzinfo is None:

            timestamp = timestamp.replace(
                tzinfo=timezone.utc
            )

        now = datetime.now(
            timezone.utc
        )

        age_seconds = (
            now - timestamp
        ).total_seconds()

        age_days = max(
            0.0,
            age_seconds / 86400.0,
        )

        # Exponential decay.
        #
        # 14 days old ≈ 50%
        # 28 days old ≈ 25%

        decay = (
            0.5
            ** (
                age_days
                / RECENCY_HALF_LIFE_DAYS
            )
        )

        return max(
            0.05,
            min(
                decay,
                1.0,
            ),
        )

    except Exception:

        return 1.0


# ============================================================
# LOAD USER INTERACTIONS
#
# IMPORTANT:
# This performs ONE database query instead of repeatedly
# querying Product for every interaction.
# ============================================================

def get_user_interaction_data(
    db,
    user_id: str,
):

    rows = (
        db.query(
            UserInteraction,
            Product,
        )
        .join(
            Product,
            UserInteraction.product_id
            == Product.product_id,
        )
        .filter(
            UserInteraction.user_id
            == user_id
        )
        .all()
    )

    return rows


# ============================================================
# BUILD USER PREFERENCES
# ============================================================

def build_user_preferences(
    rows,
):

    product_scores = {}

    category_scores = {}

    product_objects = {}

    for interaction, product in rows:

        interaction_type = (
            interaction.interaction_type
            or "view"
        )

        base_weight = (
            INTERACTION_WEIGHTS.get(
                interaction_type,
                1.0,
            )
        )

        recency_weight = (
            calculate_recency_weight(
                interaction.timestamp
            )
        )

        final_weight = (
            base_weight
            * recency_weight
        )

        product_id = (
            interaction.product_id
        )

        product_scores[
            product_id
        ] = (
            product_scores.get(
                product_id,
                0.0,
            )
            + final_weight
        )

        product_objects[
            product_id
        ] = product

        if product.category:

            category_scores[
                product.category
            ] = (
                category_scores.get(
                    product.category,
                    0.0,
                )
                + final_weight
            )

    preferences = sorted(
        product_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return (
        preferences,
        category_scores,
        product_objects,
    )


# ============================================================
# BUILD USER EMBEDDING
#
# Instead of creating one giant text string, we encode the
# user's strongest interacted products and create a weighted
# average embedding.
#
# This is both cleaner and more semantically meaningful.
# ============================================================

def build_user_embedding(
    preferences,
    product_objects,
):

    if not preferences:

        return None

    model = get_embedding_model()

    selected_products = []

    selected_weights = []

    # Only strongest 10 interactions are needed.
    # This keeps recommendation generation fast.

    for product_id, score in preferences[:10]:

        product = product_objects.get(
            product_id
        )

        if not product:

            continue

        text_parts = [
            product.product_name or "",
            product.brand or "",
            product.category or "",
            product.description or "",
            product.search_text or "",
        ]

        product_text = " ".join(
            part.strip()
            for part in text_parts
            if part
            and str(part).strip()
        )

        if not product_text:

            continue

        selected_products.append(
            product_text
        )

        selected_weights.append(
            float(score)
        )

    if not selected_products:

        return None

    embeddings = model.encode(
        selected_products,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    ).astype(np.float32)

    weights = np.asarray(
        selected_weights,
        dtype=np.float32,
    )

    weight_sum = float(
        weights.sum()
    )

    if weight_sum <= 0:

        weights = np.ones(
            len(selected_products),
            dtype=np.float32,
        )

        weight_sum = float(
            weights.sum()
        )

    user_embedding = (
        embeddings * weights[:, None]
    ).sum(
        axis=0
    ) / weight_sum

    user_embedding = normalize_vector(
        user_embedding
    )

    return user_embedding.astype(
        np.float32
    )


# ============================================================
# SEARCH FAISS
# ============================================================

def search_faiss_candidates(
    user_embedding,
    interacted_product_ids,
    limit,
):

    index = get_faiss_index()

    faiss_product_ids = (
        get_faiss_product_ids()
    )

    if index.ntotal == 0:

        return {}


    candidate_count = min(
        max(
            limit
            * FAISS_CANDIDATE_MULTIPLIER,
            MIN_FAISS_CANDIDATES,
        ),
        MAX_FAISS_CANDIDATES,
        index.ntotal,
    )


    query = np.asarray(
        [user_embedding],
        dtype=np.float32,
    )


    # The embeddings are normalized.
    #
    # For IndexFlatIP / inner product:
    # similarity = cosine similarity.
    #
    # For L2:
    # convert normalized-vector distance
    # back into cosine similarity.

    distances, indices = (
        index.search(
            query,
            candidate_count,
        )
    )


    similarity_scores = {}

    interacted_set = set(
        interacted_product_ids
    )


    for distance, vector_index in zip(
        distances[0],
        indices[0],
    ):

        if vector_index < 0:

            continue

        if (
            vector_index
            >= len(faiss_product_ids)
        ):

            continue


        product_id = (
            faiss_product_ids[
                vector_index
            ]
        )


        # Don't recommend products the
        # user has already interacted with.

        if product_id in interacted_set:

            continue


        distance = float(
            distance
        )


        if (
            index.metric_type
            == faiss.METRIC_INNER_PRODUCT
        ):

            similarity = distance

        else:

            # For normalized vectors:
            #
            # ||a-b||² = 2 - 2*cosine
            #
            # therefore:
            #
            # cosine = 1 - distance² / 2

            similarity = (
                1.0
                - (
                    distance * distance
                    / 2.0
                )
            )


        similarity = max(
            -1.0,
            min(
                similarity,
                1.0,
            ),
        )


        # Convert cosine [-1, 1]
        # to [0, 1].

        similarity = (
            similarity + 1.0
        ) / 2.0


        similarity_scores[
            product_id
        ] = float(
            similarity
        )


    return similarity_scores


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def normalize_rating(
    rating
):

    if rating is None:

        return 0.0

    try:

        return max(
            0.0,
            min(
                float(rating) / 5.0,
                1.0,
            ),
        )

    except Exception:

        return 0.0


def normalize_recommendation_score(
    score
):

    if score is None:

        return 0.0

    try:

        value = float(
            score
        )

        return max(
            0.0,
            min(
                value,
                1.0,
            ),
        )

    except Exception:

        return 0.0


def normalize_popularity(
    quantity_sold
):

    if quantity_sold is None:

        return 0.0

    try:

        value = float(
            quantity_sold
        )

        # Log scaling prevents extremely
        # popular products from dominating.

        value = math.log1p(
            max(
                value,
                0.0,
            )
        ) / math.log1p(
            10000
        )

        return max(
            0.0,
            min(
                value,
                1.0,
            ),
        )

    except Exception:

        return 0.0


# ============================================================
# CATEGORY MATCH SCORE
# ============================================================

def calculate_category_score(
    product,
    category_scores,
    max_category_score,
):

    if (
        not product.category
        or max_category_score <= 0
    ):

        return 0.0

    score = category_scores.get(
        product.category,
        0.0,
    )

    return max(
        0.0,
        min(
            score / max_category_score,
            1.0,
        ),
    )


# ============================================================
# FINAL PERSONALIZED RECOMMENDATIONS
# ============================================================

def get_personalized_recommendations(
    db,
    user_id: str,
    limit: int = DEFAULT_LIMIT,
):

    limit = min(
        max(
            int(limit),
            1,
        ),
        MAX_LIMIT,
    )


    # ========================================================
    # LOAD USER HISTORY
    # ========================================================

    rows = get_user_interaction_data(
        db=db,
        user_id=user_id,
    )


    # ========================================================
    # COLD START
    #
    # If the user has no interactions, return strong general
    # products without running the embedding model.
    # ========================================================

    if not rows:

        products = (
            db.query(Product)
            .order_by(
                desc(
                    Product.recommendation_score
                ),
                desc(
                    Product.rating
                ),
                desc(
                    Product.quantity_sold
                ),
            )
            .limit(limit)
            .all()
        )


        for product in products:

            product.similarity_score = 0.0

            product.final_recommendation_score = (
                normalize_recommendation_score(
                    product.recommendation_score
                )
            )


        return products


    # ========================================================
    # USER PREFERENCES
    # ========================================================

    (
        preferences,
        category_scores,
        product_objects,
    ) = build_user_preferences(
        rows
    )


    if not preferences:

        products = (
            db.query(Product)
            .order_by(
                desc(
                    Product.recommendation_score
                ),
                desc(
                    Product.rating
                ),
                desc(
                    Product.quantity_sold
                ),
            )
            .limit(limit)
            .all()
        )


        for product in products:

            product.similarity_score = 0.0

            product.final_recommendation_score = (
                normalize_recommendation_score(
                    product.recommendation_score
                )
            )


        return products


    # ========================================================
    # INTERACTED PRODUCT IDS
    # ========================================================

    interacted_product_ids = {
        product_id
        for product_id, score
        in preferences
    }


    # ========================================================
    # USER EMBEDDING
    # ========================================================

    user_embedding = build_user_embedding(
        preferences=preferences,
        product_objects=product_objects,
    )


    if user_embedding is None:

        return []


    # ========================================================
    # FAST FAISS RETRIEVAL
    #
    # Instead of loading all products:
    #
    # 10,000 products
    #       ↓
    # FAISS
    #       ↓
    # only ~100-500 candidates
    #
    # ========================================================

    similarity_scores = (
        search_faiss_candidates(
            user_embedding=user_embedding,
            interacted_product_ids=(
                interacted_product_ids
            ),
            limit=limit,
        )
    )


    if not similarity_scores:

        return []


    # ========================================================
    # FETCH ONLY FAISS CANDIDATES
    # ========================================================

    candidate_ids = list(
        similarity_scores.keys()
    )


    candidates = (
        db.query(Product)
        .filter(
            Product.product_id.in_(
                candidate_ids
            )
        )
        .all()
    )


    if not candidates:

        return []


    # ========================================================
    # CATEGORY NORMALIZATION
    # ========================================================

    max_category_score = max(
        category_scores.values(),
        default=1.0,
    )


    # ========================================================
    # SCORE CANDIDATES
    #
    # Semantic similarity = 55%
    # Category preference  = 20%
    # Product score        = 10%
    # Rating               = 10%
    # Popularity            = 5%
    #
    # ========================================================

    scored_products = []


    for product in candidates:

        semantic_score = (
            similarity_scores.get(
                product.product_id,
                0.0,
            )
        )


        category_score = (
            calculate_category_score(
                product=product,
                category_scores=category_scores,
                max_category_score=(
                    max_category_score
                ),
            )
        )


        recommendation_score = (
            normalize_recommendation_score(
                product.recommendation_score
            )
        )


        rating_score = (
            normalize_rating(
                product.rating
            )
        )


        popularity_score = (
            normalize_popularity(
                product.quantity_sold
            )
        )


        final_score = (

            semantic_score
            * 0.55

            + category_score
            * 0.20

            + recommendation_score
            * 0.10

            + rating_score
            * 0.10

            + popularity_score
            * 0.05

        )


        product.similarity_score = float(
            semantic_score
        )


        product.final_recommendation_score = (
            float(
                final_score
            )
        )


        scored_products.append(
            (
                product,
                final_score,
            )
        )


    # ========================================================
    # SORT
    # ========================================================

    scored_products.sort(
        key=lambda item: item[1],
        reverse=True,
    )


    # ========================================================
    # DIVERSITY
    #
    # Avoid showing 10 almost identical products.
    # Maximum 4 products from the same category in the
    # first recommendation set.
    # ========================================================

    selected_products = []

    category_counts = {}

    max_per_category = 4


    # First pass: diverse recommendations.

    for product, score in scored_products:

        category = (
            product.category
            or "Unknown"
        )


        count = category_counts.get(
            category,
            0,
        )


        if count >= max_per_category:

            continue


        selected_products.append(
            product
        )


        category_counts[
            category
        ] = count + 1


        if len(
            selected_products
        ) >= limit:

            break


    # ========================================================
    # FALLBACK
    #
    # If diversity rules didn't produce enough products,
    # fill remaining slots by score.
    # ========================================================

    if len(
        selected_products
    ) < limit:

        selected_ids = {
            product.product_id
            for product
            in selected_products
        }


        for product, score in scored_products:

            if (
                product.product_id
                in selected_ids
            ):

                continue


            selected_products.append(
                product
            )


            if len(
                selected_products
            ) >= limit:

                break


    return selected_products
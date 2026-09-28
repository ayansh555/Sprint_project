from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.products import router as products_router
from app.api.search import router as search_router
from app.api.recommendations import router as recommendations_router
from app.api.auth import router as auth_router
from app.api.interactions import router as interactions_router


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="AI E-Commerce Search & Recommendation System",
    description=(
        "AI-powered semantic product search "
        "and personalized recommendation system"
    ),
    version="1.0.0"
)


# =========================================================
# CORS CONFIGURATION
# =========================================================

app.add_middleware(
    CORSMiddleware,

    # Allow frontend during development
    allow_origins=["*"],

    allow_credentials=False,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================================
# API ROUTES
# =========================================================

# Product APIs
app.include_router(products_router)

# Semantic search APIs
app.include_router(search_router)

# Recommendation APIs
app.include_router(recommendations_router)

# Authentication APIs
app.include_router(auth_router)

# User interaction APIs
app.include_router(interactions_router)


# =========================================================
# ROOT ENDPOINT
# =========================================================

@app.get("/")
def root():
    return {
        "message": "AI E-Commerce API is running",
        "version": "1.0.0"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
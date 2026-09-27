from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.products import router as products_router
from app.api.search import router as search_router
from app.api.recommendations import router as recommendations_router


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

    # Allow the local frontend during development
    allow_origins=["*"],

    allow_credentials=False,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================================
# API ROUTES
# =========================================================

app.include_router(products_router)

app.include_router(search_router)

app.include_router(recommendations_router)


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
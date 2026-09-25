from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):

    user_id: str = Field(
        ...,
        min_length=1
    )

    limit: int = Field(
        default=10,
        ge=1,
        le=50
    )
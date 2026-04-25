from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class FeedbackRating(str, Enum):
    like = "like"
    dislike = "dislike"


class FeedbackCreate(BaseModel):
    project_id: int = Field(..., gt=0)
    request_id: str = Field(..., min_length=6, max_length=64)
    rating: FeedbackRating
    comment: Optional[str] = Field(default=None, max_length=500)


class FeedbackResponse(BaseModel):
    id: int
    project_id: int
    request_id: str
    rating: FeedbackRating
    comment: Optional[str]

    class Config:
        from_attributes = True

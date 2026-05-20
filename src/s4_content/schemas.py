from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .models import TicketStatusEnum

# TICKETS
class TicketBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=100, description="The summary of the ticket/issue")
    description: str = Field(..., min_length=10, description="Detailed explanation of the issue")

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    status: Optional[TicketStatusEnum] = None

class TicketOut(TicketBase):
    id: int
    user_id: int
    status: TicketStatusEnum
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# POSTS (News/Blogs)
class PostBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    content: str
    is_published: bool = False

class PostCreate(PostBase):
    pass

class PostOut(PostBase):
    id: int
    author_id: int
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# REVIEWS
class ReviewBase(BaseModel):
    tour_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewOut(ReviewBase):
    id: int
    user_id: int
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
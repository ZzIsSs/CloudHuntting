from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .models import TicketStatusEnum, ArticleTypeEnum

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
        from_attributes = True

# TICKET MESSAGES
class MessageBase(BaseModel):
    message: str = Field(..., min_length=1, description="Message content")

class MessageCreate(MessageBase):
    pass

class MessageOut(MessageBase):
    id: int
    ticket_id: int
    sender_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TicketDetailOut(BaseModel):
    ticket: TicketOut
    messages: List[MessageOut]

# POSTS (News/Blogs)
class PostBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    content: str
    article_type: ArticleTypeEnum = ArticleTypeEnum.POST
    is_published: bool = False

class PostCreate(PostBase):
    pass

class PostOut(PostBase):
    id: int
    author_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# REVIEWS
class ReviewBase(BaseModel):
    location_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewOut(ReviewBase):
    id: int
    user_id: int
    is_approved: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ReviewDetailOut(ReviewOut):
    username: str


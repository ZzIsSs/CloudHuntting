from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from . import schemas, models
from src.shared.database import get_db
from src.s3_auth.dependencies import get_current_user
from src.s3_auth.models import User, RoleEnum

router = APIRouter(prefix="/content", tags=["Content & CSKH"])

# TICKETS (CSKH)

@router.post("/tickets", response_model=schemas.TicketOut, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket_in: schemas.TicketCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_ticket = models.Ticket(
        user_id=current_user.id,
        title=ticket_in.title,
        description=ticket_in.description
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket

@router.get("/tickets", response_model=List[schemas.TicketOut])
def get_tickets(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(models.Ticket)
    
    # RBAC: Normal users can only see their own tickets
    if current_user.role == RoleEnum.user:
        query = query.filter(models.Ticket.user_id == current_user.id)
        
    tickets = query.offset(skip).limit(limit).all()
    return tickets

@router.get("/tickets/{ticket_id}", response_model=schemas.TicketDetailOut)
def get_ticket_details(
    ticket_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    # RBAC: Normal users can only see their own tickets
    if current_user.role == RoleEnum.user and ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions to view this ticket")
        
    messages = db.query(models.TicketMessage).filter(models.TicketMessage.ticket_id == ticket_id).order_by(models.TicketMessage.created_at).all()
    
    return schemas.TicketDetailOut(ticket=ticket, messages=messages)

@router.post("/tickets/{ticket_id}/messages", response_model=schemas.MessageOut, status_code=status.HTTP_201_CREATED)
def create_ticket_message(
    ticket_id: int, 
    message_in: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    # RBAC: Normal users can only reply to their own tickets
    if current_user.role == RoleEnum.user and ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions to reply to this ticket")
        
    new_message = models.TicketMessage(
        ticket_id=ticket_id,
        sender_id=current_user.id,
        message=message_in.message
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

@router.put("/tickets/{ticket_id}", response_model=schemas.TicketOut)
def update_ticket_status(
    ticket_id: int, 
    ticket_in: schemas.TicketUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # RBAC: Only admins or moderators can update ticket status
    if current_user.role not in [RoleEnum.admin, RoleEnum.moderator]:
        raise HTTPException(status_code=403, detail="Not enough permissions to update ticket status")

    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if ticket_in.status:
        ticket.status = ticket_in.status
        db.commit()
        db.refresh(ticket)
        
    return ticket

# POSTS / NEWS

@router.post("/posts", response_model=schemas.PostOut, status_code=status.HTTP_201_CREATED)
def create_post(
    post_in: schemas.PostCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_post = models.Post(
        author_id=current_user.id,
        **post_in.dict()
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/posts", response_model=List[schemas.PostOut])
def get_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    # Public endpoint: No auth required to view published posts
    posts = db.query(models.Post).filter(models.Post.is_published == True).offset(skip).limit(limit).all()
    return posts

@router.get("/posts/{post_id}", response_model=schemas.PostOut)
def get_post_details(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    # RBAC: Only author or admin can delete
    if current_user.role != RoleEnum.admin and post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions to delete this post")
        
    db.delete(post)
    db.commit()
    return None

# REVIEWS

@router.post("/reviews", response_model=schemas.ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(
    review_in: schemas.ReviewCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_review = models.Review(
        user_id=current_user.id,
        **review_in.dict()
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

@router.get("/reviews/location/{location_id}", response_model=List[schemas.ReviewOut])
def get_location_reviews(location_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    # Public endpoint: No auth required to view reviews
    reviews = db.query(models.Review).filter(models.Review.location_id == location_id).offset(skip).limit(limit).all()
    return reviews

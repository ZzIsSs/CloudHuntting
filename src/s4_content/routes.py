from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from . import schemas, models
from shared.database import get_db

router = APIRouter(prefix="/content", tags=["Content & CSKH"])

# TICKETS (CSKH)

@router.post("/tickets", response_model=schemas.TicketOut, status_code=status.HTTP_201_CREATED)
def create_ticket(ticket_in: schemas.TicketCreate, db: Session = Depends(get_db)):
    # Note: Using hardcoded user_id=1 for now. 
    # In the future, replace this with auth dependency (e.g., get_current_user)
    current_user_id = 1 
    
    new_ticket = models.Ticket(
        user_id=current_user_id,
        title=ticket_in.title,
        description=ticket_in.description
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket

@router.get("/tickets", response_model=List[schemas.TicketOut])
def get_tickets(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    tickets = db.query(models.Ticket).offset(skip).limit(limit).all()
    return tickets

@router.put("/tickets/{ticket_id}", response_model=schemas.TicketOut)
def update_ticket_status(ticket_id: int, ticket_in: schemas.TicketUpdate, db: Session = Depends(get_db)):
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
def create_post(post_in: schemas.PostCreate, db: Session = Depends(get_db)):
    # Note: Hardcoded author_id
    current_user_id = 1 
    new_post = models.Post(
        author_id=current_user_id,
        **post_in.dict()
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/posts", response_model=List[schemas.PostOut])
def get_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    posts = db.query(models.Post).filter(models.Post.is_published == True).offset(skip).limit(limit).all()
    return posts

# REVIEWS

@router.post("/reviews", response_model=schemas.ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(review_in: schemas.ReviewCreate, db: Session = Depends(get_db)):
    # Note: Hardcoded user_id
    current_user_id = 1 
    new_review = models.Review(
        user_id=current_user_id,
        **review_in.dict()
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

@router.get("/reviews/tour/{tour_id}", response_model=List[schemas.ReviewOut])
def get_tour_reviews(tour_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    reviews = db.query(models.Review).filter(models.Review.tour_id == tour_id).offset(skip).limit(limit).all()
    return reviews
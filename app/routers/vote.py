import time
from .. import models, schemas, utils, oauth2
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(
    prefix="/vote",
    tags=["Vote"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote:schemas.Vote, db: Session = Depends(get_db), 
current_user: schemas.TokenData = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    vote_query = db.query(models.Vote).filter(models.Vote.user_id == 
        current_user.id).filter(models.Vote.post_id == vote.post_id)
    found_vote = vote_query.first()
    
    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
            detail="You have already voted")
        new_vote = models.Vote(user_id=current_user.id, post_id=vote.post_id)
        db.add(new_vote)
        db.commit()
        return {"message": "Vote created"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
            detail="Vote is not exist")
        vote_query.delete()
        db.commit()
        return {"message": "Vote deleted"}
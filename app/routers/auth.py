from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, utils, database, oauth2

router = APIRouter(
    tags = ["Auth"]
)

@router.post("/login", response_model=schemas.Token)
def login(user_cred:schemas.UserLogin,db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_cred.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not utils.verify(user_cred.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    # Create a JWT token for the user
    # return a token 
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
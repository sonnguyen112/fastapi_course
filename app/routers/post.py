from pyexpat import model
from .. import models, schemas,oauth2
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List, Optional
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.get("/", response_model=List[schemas.PostOut]) 
def get_posts(db: Session = Depends(get_db), 
current_user: schemas.TokenData = Depends(oauth2.get_current_user),
limit:int=10, skip:int=0, search:str=""):
    # cursor.execute("SELECT * FROM posts")
    # posts = cursor.fetchall()
    # print(posts)
    # posts = db.query(models.Post).filter(models.Post.title.contains(
    #     search)).limit(limit).offset(skip).all()

    posts = db.query(models.Post, func.count(models.Vote.post_id
    ).label("votes")).join(models.Vote, 
    models.Vote.post_id == models.Post.id, isouter=True).group_by(
        models.Post.id).filter(
        models.Post.title.contains(
        search)).limit(limit).offset(skip).all()
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, 
db: Session = Depends(get_db),current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    # cursor.execute("""insert into posts (title, content, publish, rating) values 
    # (%s,%s,%s,%s) returning *""",(post.title, post.content, 
    # post.publish, post.rating))
    # new_post = cursor.fetchone()
    # conn.commit()

    # new_post = models.Post(title=post.title, content=post.content,published=post.publish)
    
    new_post = models.Post(owner_id=current_user.id,**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{post_id}", response_model=schemas.PostOut)
def get_post(post_id: int, response: Response, 
db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    # cursor.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
    # post = cursor.fetchone()

    # post = db.query(models.Post).filter(models.Post.id == post_id).first()
    post = db.query(models.Post, func.count(models.Vote.post_id
    ).label("votes")).join(models.Vote, 
    models.Vote.post_id == models.Post.id, isouter=True).group_by(
        models.Post.id).filter(models.Post.id == post_id).first()
    if not post:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"data" : "Post not found"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post[0].owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for perform action")
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    # cursor.execute("DELETE FROM posts WHERE id = %s returning *", 
    # (post_id,))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    deleted_post = post_query.first()
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if deleted_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform action")
    post_query.delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{post_id}", status_code=status.HTTP_200_OK, response_model=schemas.Post)
def update_post(post_id: int, post: schemas.PostCreate, db: Session = Depends(get_db),
current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    # cursor.execute("UPDATE posts SET title = %s, content = %s, publish = %s, rating = %s WHERE id = %s returning *",
    # (post.title, post.content, post.publish, post.rating, post_id))
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    updated_post = post_query.first()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if updated_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform action")
    post_query.update(post.dict())
    db.commit()
    return updated_post

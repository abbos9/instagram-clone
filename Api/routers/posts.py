from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Path, status
from sqlalchemy.orm import Session
from models.auth_models import UsersTable
from models.posts_model import PostCommentTable, PostLikeTable, PostTable
from schemas.posts_chema import (CommentSchema, CreateCommentSchema, DeleteSchema, UpdateSchema, PostSchema,CommentDeleteSchema,
ResponsePostSchema,CommentUpdateSchema, LikeSchema)
from database import get_db
from utils.auth_utils import JWTBearer, JWTHandler
import shutil
import os
import uuid

router = APIRouter(
    prefix='/post',
    tags=['posts']
)

db_dependency = Annotated[Session, Depends(get_db)]

# POSTS

# Read all posts
@router.get("/", response_model=list[ResponsePostSchema])
async def get_posts(db:db_dependency):
    posts = db.query(PostTable).all()
    return posts

# Read a single post by ID
@router.get("/{post_id}", response_model=ResponsePostSchema)
async def get_post(db:db_dependency,post_id: int = Path(...)):
    post = db.query(PostTable).filter(PostTable.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


# Create a new post
@router.post("/", response_model=ResponsePostSchema)
async def create_post(
    description: str,
    db: Session = Depends(db_dependency),  # Ensure correct import and type annotation
    file: UploadFile = File(...),
    user: UsersTable = Depends(JWTBearer())
):
    file_dir = "media/"
    os.makedirs(file_dir, exist_ok=True)
    
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_location = os.path.join(file_dir, unique_filename)
    
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"File saving error: {e}"
        )

    new_post = PostTable(
        user_id=user.id,
        description=description,
        file=unique_filename
    )
    
    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Database error: {e}"
        )

    return new_post


# Update a post by ID
@router.put("/{post_id}", response_model=ResponsePostSchema)
async def update_post(
    db: db_dependency,
    post_id: int = Path(...),
    description: str = None,
    file: UploadFile = File(None),
    user: UsersTable = Depends(JWTBearer())
):
    post = db.query(PostTable).filter(PostTable.id == post_id).first()
    
    if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this post")

    if description is not None:
        post.description = description

    if file is not None:
        file_dir = "media/"
        os.makedirs(file_dir, exist_ok=True)
        
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_location = os.path.join(file_dir, unique_filename)
        
        try:
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"File saving error: {e}")

        post.file = unique_filename
    try:
        db.commit()
        db.refresh(post)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

    return post

# Delete a post by ID
@router.delete("/{post_id}", response_model=dict)
async def delete_post(
    db: db_dependency, 
    post_id: int = Path(...),                
    user: UsersTable = Depends(JWTBearer())):
    post = db.query(PostTable).filter(PostTable.id == post_id).first()
    
    if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this post")

    
    try:
        db.delete(post)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

    return {"detail": "Post deleted successfully"}


# COMMENTS

# Write comments
@router.post("/comment", response_model=CreateCommentSchema)
async def write_comment(posts_schema:CreateCommentSchema,db:db_dependency,user: UsersTable = Depends(JWTBearer())):
    post = db.query(PostTable).filter(PostTable.id == posts_schema.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    new_comment = PostCommentTable(
        user_id = user.id,
        post_id=posts_schema.post_id,
        comment = posts_schema.comment
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


# Update comment
@router.put('/comment/{comment_id}', response_model=CommentUpdateSchema)
async def update_comment(
    comment_update: CommentUpdateSchema,
    db: db_dependency,
    comment_id: int,
    user: UsersTable = Depends(JWTBearer())
):
    comment = db.query(PostCommentTable).filter(PostCommentTable.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if comment.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this comment")

    comment.comment = comment_update.comment
    
    try:
        db.commit()
        db.refresh(comment)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

    return comment


# Delete comment
@router.delete("/comment/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: int,
    db: db_dependency,
    user: UsersTable = Depends(JWTBearer())
):
    comment = db.query(PostCommentTable).filter(PostCommentTable.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if comment.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this comment")

    try:
        db.delete(comment)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    return {"message": "Comment deleted successfully"}

# get comment
@router.get("/posts/{post_id}/comment", response_model=list[CommentSchema])
async def get_comments(post_id: int, db: db_dependency):
    comments = db.query(PostCommentTable).filter(PostCommentTable.post_id == post_id).all()

    if not comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No comments found for this post")

    return comments


# LIKE

# Create like

@router.post('/like/{post_id}/', response_model=LikeSchema)
async def create_like(db:db_dependency,post_id:int,user:UsersTable = Depends(JWTBearer())):
    post = db.query(PostTable).filter(PostTable.id == post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    existing_like = db.query(PostLikeTable).filter(PostLikeTable.post_id == post_id, PostLikeTable.user_id == user.id).first()

    if existing_like:
        db.delete(existing_like)
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Like is Deleted')


    new_like = PostLikeTable(
        user_id = user.id,
        post_id=post.id,
    )
    if not existing_like:
        db.add(new_like)
        db.commit()
        db.refresh(new_like)

    return new_like

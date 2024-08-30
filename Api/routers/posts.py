from typing import Annotated
from fastapi import APIRouter, Body, Depends, Form, HTTPException, File, UploadFile, Path, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.auth_models import UsersTable
from models.posts_model import PostCommentTable, PostLikeTable, PostSaveTable, PostTable
from schemas.posts_chema import (BaseCommentSchema, CommentSchema, CreateCommentSchema, DeleteSchema, SaveSchema, UpdateSchema, PostSchema,CommentDeleteSchema,
ResponsePostSchema,CommentUpdateSchema, LikeSchema, BaseResponseSchema, UuidSchema)
from database import get_db
from utils.auth_utils import JWTBearer, JWTHandler
import shutil
import os
from fastapi.responses import FileResponse
import uuid
from general_api.descriptions import create_post_desc_post, create_post_desc
router = APIRouter(
    prefix='/post',
    tags=['posts']
)

db_dependency = Annotated[Session, Depends(get_db)]

# POSTS

# Read all posts
@router.get("/", response_model=list[ResponsePostSchema], description=create_post_desc, )
async def get_posts(db:db_dependency,user: UsersTable = Depends(JWTBearer())):
    posts = db.execute(select(PostTable).join(UsersTable).where(PostTable.user_id == user.id)).scalars().all()
    return posts

# Read a single post by ID
@router.post("/{post_id}", response_model=ResponsePostSchema)
async def get_post(db:db_dependency,post:BaseResponseSchema, ):
    post = db.execute(select(PostTable).join(UsersTable).where(PostTable.id == post.id)).scalar()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post

@router.post("/image/")
def get_img(image_request: UuidSchema):
    filepath = os.path.join('media/', os.path.basename(str(image_request.uuid)))
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(filepath)


@router.post("/", response_model=ResponsePostSchema,description=create_post_desc_post)
async def create_post(
    db: db_dependency,
    description: str = Form(...),
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"File saving error: {e}")

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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

    return new_post

# Update a post by ID
@router.put("/{post_id}", response_model=ResponsePostSchema,)
async def update_post(
    db: db_dependency,
    post_id: int = Path(...),
    description: str = Form(...),
    file: UploadFile = File(None),
    user: UsersTable = Depends(JWTBearer())
):
    post = db.query(PostTable).join(UsersTable).filter(PostTable.id == post_id).first()
    
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
    schema: DeleteSchema,                
    user: UsersTable = Depends(JWTBearer())):
    post = db.query(PostTable).filter(PostTable.id == schema.post_id).first()
    
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
    user: UsersTable = Depends(JWTBearer())
):
    comment = db.query(PostCommentTable).filter(PostCommentTable.id == comment_update.id).first()

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
    comment_schema:CommentDeleteSchema,
    db: db_dependency,
    user: UsersTable = Depends(JWTBearer())
):
    comment = db.query(PostCommentTable).filter(PostCommentTable.id == comment_schema.id).first()

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
@router.post("/{post_id}/comment", response_model=list[CommentSchema])
async def get_comments(schema: BaseCommentSchema, db: db_dependency):
    comments = db.execute(select(PostCommentTable).where(PostCommentTable.post_id == schema.id)).scalars().all()

    if not comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No comments found for this post")

    return comments


# LIKE

# Create like

@router.post('/like/{post_id}/', response_model=LikeSchema)
async def create_like(db:db_dependency,schema:LikeSchema,user:UsersTable = Depends(JWTBearer())):
    post = db.execute(select(PostTable).where(PostTable.id == schema.post_id)).scalar()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    existing_like = db.execute(select(PostLikeTable).where(PostLikeTable.post_id == schema.post_id, PostLikeTable.user_id == user.id)).scalar()

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

# Get user's liked posts
@router.get('/user/likes', response_model=list[ResponsePostSchema])
async def user_like(
    db: db_dependency,
    user: UsersTable = Depends(JWTBearer())
):
    
    liked_posts = db.execute(select(PostTable).join(PostLikeTable,).where(PostLikeTable.user_id == user.id)).scalars().all()

    return liked_posts


# Save

@router.post("/save/post", response_model=SaveSchema)
async def create_save(db: db_dependency, schema: SaveSchema, user: UsersTable = Depends(JWTBearer())):
    post = db.execute(select(PostTable).where(PostTable.id == schema.post_id)).scalar()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=" post not found" )



    saved_post = db.execute(select(PostSaveTable).where(PostSaveTable.post_id == schema.post_id, PostSaveTable.user_id == user.id)).scalar()
    

    if saved_post:
        db.delete(saved_post)
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Unsaved')


    new_save = PostSaveTable(
        user_id = user.id,
        post_id= schema.post_id
    )
    db.add(new_save)
    db.commit()
    db.refresh(new_save)

    return new_save




@router.get('/saved/', response_model=list[ResponsePostSchema])
async def get_saved_posts(db:db_dependency, user: UsersTable = Depends(JWTBearer())):

    saved_posts = db.execute(select(PostTable).join(PostSaveTable,).where(PostSaveTable.user_id == user.id)).scalars().all()

    return saved_posts
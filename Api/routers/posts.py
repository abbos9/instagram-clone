from typing import Annotated
import aiofiles
from fastapi import APIRouter, Depends, Form, HTTPException, File, UploadFile, Path, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from directories.posts import create_dir as post_create_dir
from models.auth_models import UsersTable
from models.posts_model import PostCommentTable, PostLikeTable, PostSaveTable, PostTable
from schemas.posts_chema import (BaseCommentSchema, CommentSchema, CreateCommentSchema, DeleteSchema, SaveSchema, UpdateSchema, PostSchema,CommentDeleteSchema,
ResponsePostSchema,CommentUpdateSchema, LikeSchema, BaseResponseSchema, UuidSchema)
from database import get_db
from utils.auth_utils import JWTBearer, JWTHandler
from fastapi.responses import FileResponse
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
@router.post("/{post_id}/", response_model=ResponsePostSchema)
async def get_post(db:db_dependency,post:BaseResponseSchema, ):
    post = db.execute(select(PostTable).join(UsersTable).where(PostTable.id == post.id)).scalar()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post



# @router.post("/image/")
# def get_img(image_request: UuidSchema):
#     filepath = os.path.join('media/', os.path.basename(str(image_request.uuid)))
    
#     if not os.path.exists(filepath):
#         raise HTTPException(status_code=404, detail="Image not found")
    
#     return FileResponse(filepath)


@router.post("/", description=create_post_desc_post)
async def create_posts(
    session: db_dependency,
    file: UploadFile = File(...),
    description: str = Form(...),
    user: UsersTable = Depends(JWTBearer()),
    ):
    
    post = PostTable(
        user_id=user.id,
        file=None,
        description=description,
    )
    session.add(post)
    session.flush()
    file_dir_for_django = None
    if file is not None:
        file_data = await post_create_dir(post_id=post.id, filename=file.filename)
        content = file.file.read()
        async with aiofiles.open(file_data['file_full_path'], 'wb') as out_file:
            file_dir_for_django = file_data['file_dir'] + file.filename
            await out_file.write(content)
    post.file = file_dir_for_django
    session.commit()
    session.refresh(post)

    return {
        "message": "Created !"
    }


# Update a post by ID
@router.patch("/{post_id}/")
async def update_post(
    session: db_dependency,
    post_id: int= Path(...),
    file: UploadFile = File(None),
    description: str = Form(None),
    user: UsersTable = Depends(JWTBearer())
):
    # Step 1: Fetch the existing post by ID
    post = session.query(PostTable).filter(PostTable.id == post_id, PostTable.user_id == user.id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found or you're not authorized to update this post")

    if post.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this post")


    # Step 2: Update the description if provided
    if description:
        post.description = description

    file_dir_for_django = post.file  # Keep the current file path if no new file is provided

    # Step 3: Process the uploaded file (if provided)
    if file is not None:
        file_data = await post_create_dir(post_id=post.id, filename=file.filename)
        try:
            # Read the file asynchronously
            content = await file.read()

            # Write the file asynchronously
            async with aiofiles.open(file_data['file_full_path'], 'wb') as out_file:
                await out_file.write(content)

            file_dir_for_django = file_data['file_dir'] + file.filename  # Update the file path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

    # Step 4: Update the file path and commit the changes
    post.file = file_dir_for_django
    session.commit()
    session.refresh(post)

    return {
        "message": "Post updated successfully!"
    }
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
@router.post("/comment/", response_model=CreateCommentSchema)
async def write_comment(
                        db:db_dependency,
                        posts_schema:CreateCommentSchema,
                        user: UsersTable = Depends(JWTBearer())):

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
@router.put('/comment/{comment_id}/', response_model=CommentUpdateSchema)
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
@router.delete("/comment/{comment_id}/", status_code=204)
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
@router.post("/{post_id}/comment/", response_model=list[CommentSchema])
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
@router.get('/user/likes/', response_model=list[ResponsePostSchema])
async def user_like(
    db: db_dependency,
    user: UsersTable = Depends(JWTBearer())
):
    
    liked_posts = db.execute(select(PostTable).join(PostLikeTable,).where(PostLikeTable.user_id == user.id)).scalars().all()

    return liked_posts


# Save

@router.post("/save/post/", response_model=SaveSchema)
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
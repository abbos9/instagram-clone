from typing import List, Optional
from pydantic import BaseModel
from schemas.auth_shema import UserResponseSchema


class LikeSchema(BaseModel):
    id:int
    post_id:int
    user:Optional[UserResponseSchema] = None
    class Config:
        from_attributes = True

class BaseCommentSchema(BaseModel):
    id: Optional[int] = None

class CommentSchema(BaseCommentSchema):
    id: Optional[int] = None
    user_id: Optional[int] = None
    post_id: Optional[int] = None
    comment: Optional[str] = None
    user: Optional[UserResponseSchema] = None

    class Config:
        from_attributes = True

class PostSchema(BaseModel):
    description: str

class UpdateSchema(BaseModel):
    description:str
    post_id:int
    class Config:
        from_attributes = True

class DeleteSchema(BaseModel):
    post_id:int

    class Config:
        from_attributes = True



class ResponsePostSchema(BaseModel):
    id: int
    user_id: int
    description: str
    file: str
    user: UserResponseSchema
    comments: List[CommentSchema] = []
    likes:List[LikeSchema] = []

    class Config:
        from_attributes = True

class CreateCommentSchema(BaseModel):
    post_id: int
    comment: str


class CommentUpdateSchema(BaseModel):
    id:int
    comment: str
    class Config:
        from_attributes = True

class CommentDeleteSchema(BaseModel):
    id:int

    class Config:
        from_attributes = True
from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from general_api.config import Tashkent_tz
from general_api.models import BaseMode

class PostTable(BaseMode):
    __tablename__ = 'blogs_post'
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users_user.id'), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text)
    file: Mapped[str] = mapped_column(Text)

    user = relationship("UsersTable", back_populates="posts")
    comments = relationship("PostCommentTable", back_populates="post")
    likes = relationship("PostLikeTable", back_populates="post")
    saves = relationship("PostSaveTable", back_populates="post")


class PostCommentTable(BaseMode):
    __tablename__ = 'blogs_postcomment'
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users_user.id'), nullable=False, index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey('blogs_post.id'), nullable=False, index=True)
    comment: Mapped[str] = mapped_column(Text)

    user = relationship("UsersTable", back_populates="comments")
    post = relationship("PostTable", back_populates="comments")

class PostLikeTable(BaseMode):
    __tablename__ = 'blogs_postlike'
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users_user.id'), nullable=False, index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey('blogs_post.id'), nullable=False, index=True)

    user = relationship("UsersTable", back_populates="likes")
    post = relationship("PostTable", back_populates="likes")

class PostSaveTable(BaseMode):
    __tablename__ = "blogs_postsave"

    user_id: Mapped[int] = mapped_column(ForeignKey('users_user.id'))
    post_id: Mapped[int] = mapped_column(ForeignKey('blogs_post.id'))

    user = relationship("UsersTable", back_populates="saves")
    post = relationship("PostTable", back_populates="saves")
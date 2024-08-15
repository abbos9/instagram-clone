from sqlalchemy import ForeignKey, Text, UniqueConstraint,DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from general_api.config import Tashkent_tz

from database import Base




class PostTable(Base):
    __tablename__ = 'blogs_post'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True,index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users_user.id'), nullable=False,index=True)
    description: Mapped[str] = mapped_column(Text)
    file: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(tz=Tashkent_tz), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(tz=Tashkent_tz), onupdate=datetime.now(tz=Tashkent_tz), nullable=False)



    user = relationship("UsersTable", back_populates="posts")
    comments = relationship("PostCommentTable", back_populates="post")
    likes = relationship("PostLikeTable", back_populates="post")


class PostCommentTable(Base):
    __tablename__ = 'blogs_postcomment'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True,index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users_user.id'), nullable=False,index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey('blogs_post.id'), nullable=False,index=True)
    comment: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(tz=Tashkent_tz), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(tz=Tashkent_tz), onupdate=datetime.now(tz=Tashkent_tz), nullable=False)



    user = relationship("UsersTable", back_populates="comments")
    post = relationship("PostTable", back_populates="comments")

class PostLikeTable(Base):
    __tablename__ = 'blogs_postlike'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users_user.id'), nullable=False,index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey('blogs_post.id'), nullable=False,index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(tz=Tashkent_tz), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(tz=Tashkent_tz), onupdate=datetime.now(tz=Tashkent_tz), nullable=False)



    user = relationship("UsersTable", back_populates="likes")
    post = relationship("PostTable", back_populates="likes")

    __table_args__ = (UniqueConstraint('user_id', 'post_id', name='_user_post_uc'),)
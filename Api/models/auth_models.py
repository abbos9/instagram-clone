from database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from sqlalchemy import Boolean
from sqlalchemy.orm import relationship

class UsersTable(Base):
    __tablename__ = "users_user"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str]
    phone_num: Mapped[str]
    role: Mapped[str]
    date_of_birth: Mapped[date]
    gender: Mapped[str]
    date_joined: Mapped[date]
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    posts = relationship("PostTable", back_populates="user")
    comments = relationship("PostCommentTable", back_populates="user")
    likes = relationship("PostLikeTable", back_populates="user")
    saves = relationship("PostSaveTable", back_populates="user")  
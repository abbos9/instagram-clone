from sqlalchemy import Boolean, DateTime, Integer, String
from datetime import datetime
from database import Base  # Ensure this is imported correctly
from general_api.config import Tashkent_tz
from sqlalchemy.orm import Mapped, mapped_column

class UsersTable(Base):
    __tablename__ = "users"  # Ensure this matches your actual table name

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(36))
    last_name: Mapped[str] = mapped_column(String(36))
    phone_num: Mapped[str] = mapped_column(String(36), unique=True, nullable=True)
    password: Mapped[str] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String(24))
    gender: Mapped[str] = mapped_column(String(24))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(tz=Tashkent_tz))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(tz=Tashkent_tz), onupdate=datetime.now(tz=Tashkent_tz))

from database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime
from sqlalchemy import Boolean
from sqlalchemy import DateTime

from general_dj.config import Tashkent_tz

class BaseMode(Base):
    __abstract__ = True
    
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(tz=Tashkent_tz))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(tz=Tashkent_tz), onupdate=datetime.now(tz=Tashkent_tz))


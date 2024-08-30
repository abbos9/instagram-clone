from database import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime
from sqlalchemy import Boolean
from sqlalchemy import DateTime

from general_api.config import Tashkent_tz

class BaseMode(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True,index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(tz=Tashkent_tz), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(tz=Tashkent_tz), onupdate=datetime.now(tz=Tashkent_tz), nullable=False)
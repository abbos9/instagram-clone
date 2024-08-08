from fastapi import FastAPI
from database import engine
from database import Base
from models import auth_models

auth_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Instagram Api")

from routers.auth import router as auth_router


app.include_router(auth_router)
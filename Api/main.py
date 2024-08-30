from fastapi import FastAPI
from database import engine
from database import Base
from models import *
from fastapi.staticfiles import StaticFiles


Base.metadata.create_all(bind=engine)


app = FastAPI(title="Instagram Api",)


from routers.auth import router as auth_router
from routers.posts import router as post_router


app.include_router(auth_router)
app.include_router(post_router)


app.mount("/media", StaticFiles(directory="media"), name="media")
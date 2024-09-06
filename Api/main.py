from fastapi import FastAPI
from database import engine, Base
# from models import *
from fastapi.staticfiles import StaticFiles


Base.metadata.create_all(bind=engine)


app = FastAPI(title="Instagram Api")


from routers import auth
from routers import posts

app.include_router(auth.router)
app.include_router(posts.router)


# app.mount("/media", StaticFiles(directory="media"), name="media")
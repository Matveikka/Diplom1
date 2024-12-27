from fastapi import FastAPI
from backend.database import engine, Base
from routers import post
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.include_router(post.router)
Base.metadata.create_all(bind=engine)




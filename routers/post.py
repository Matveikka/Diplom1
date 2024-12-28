from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import insert, select
from backend.database import SessionLocal
from schemas.post import PostModel
from datetime import datetime
from typing import Annotated
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
async def read_posts(request: Request, db: Annotated[Session, Depends(get_db)]):
    result = await db.execute(select(PostModel))
    posts = result.scalars().all()
    return templates.TemplateResponse("home.html", {"request": request, "posts": posts})


@router.get("/posts/{post_id}", response_class=HTMLResponse, name="details")
async def read_post(post_id: int, request: Request, db: Annotated[Session, Depends(get_db)]):
    post = db.scalar(select(PostModel).where(PostModel.id == post_id))
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse("details.html", {"request": request, "post": post})


@router.post("/posts/", response_model=PostModel)
async def create_post(post: PostModel, db: Annotated[Session, Depends(get_db)]):
    new_post = insert(PostModel).values(title=post.title,
                                        rezume=post.rezume,
                                        info=post.info,
                                        created_at=datetime.now())
    db.execute(new_post)
    db.commit()
    db_post = db.query(PostModel).filter(PostModel.title == post.title).first()
    return db_post


@router.delete("/posts/{post_id}", response_model=PostModel)
async def delete_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    post_to_delete = db.scalar(PostModel).where(PostModel.id == post_id)
    if post_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post not found")
    db.delete(post_to_delete)
    db.commit()
    return {'transaction': 'Post delete is successful'}

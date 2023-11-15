from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form, Response, status, HTTPException
from sqlalchemy.orm import Session

import schemas
from controller import post
from database import SessionLocal, get_db
from auth.oauth2 import get_current_user

router = APIRouter(
    prefix="/posts",
    tags=["post"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[schemas.PostDisplay])
def get_all_posts(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    posts = post.get_all(db, current_user)
    if posts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='No posts found')
    return posts


@router.get('/packages', response_model=list[schemas.PackageResponse])
def get_all_packages(db: Session = Depends(get_db), current_user=Depends(get_current_user), page: int = 1,
                     per_page: int = 10, limit: int = 10, user_id: Optional[int] = None):
    result = post.get_all_package(db, current_user, page, user_id, per_page)
    total_line = result.get('lines')
    total_page = result.get('pages')
    lines_per_page = result.get('per_page')
    actual_page = result.get('page')
    data = result.get('data')
    return schemas.PackageResponse(lines=total_line, total_number_of_pages=total_page, lines_per_page=lines_per_page,
                                   data=data)


@router.post("/")
def submit_form(
        images: list[UploadFile] = File(...),
        reference_number: str = Form(...),
        description: str = Form(...),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    return post.create(db, images, reference_number, description, current_user)


@router.get('/{p_id}', response_model=schemas.PostDisplay)
def get_post_by_id(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return post.get_by_id(db, id, current_user)


@router.put('/{p_id}', response_model=schemas.PostDisplay)
def update_container(id: int, request: schemas.PostDisplay, db: Session = Depends(get_db),
                     current_user=Depends(get_current_user)):
    return post.update(db, id, current_user, request)


@router.delete('/{p_id}', status_code=status.HTTP_200_OK)
def delete_post(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return post.delete(db, id, current_user)

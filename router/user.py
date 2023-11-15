from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form, Response, status
from sqlalchemy.orm import Session

import schemas
from controller import users
from database import SessionLocal, get_db
from auth.oauth2 import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["user"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.on_event('startup')
def startup_event():
    with SessionLocal() as db:
        return users.create_initial_user(db)


@router.get("/", response_model=list[schemas.UserDisplay])
def get_all_users(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return users.get_all_users(db, current_user.administrator)


@router.get('/{u_id}', response_model=schemas.UserDisplay)
def get_user_by_id(u_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return users.get_user_by_id(db, u_id, current_user)


@router.get('/{u_email}', response_model=schemas.UserDisplay)
def get_user_by_email(db: Session = Depends(get_db), email: str = Form(...)):
    return users.get_user_by_email(db, email)


@router.post("/")
def submit_form(
        password: str = Form(...),
        date_of_birth: str = Form(...),
        image: UploadFile = File(...),
        active: bool = Form(...),
        administrator: bool = Form(...),
        email: str = Form(...),
        name: str = Form(...),
        middle_name: Optional[str] = Form(None),
        last_name: str = Form(...),
        position: str = Form(...),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    return users.create(db, password, date_of_birth, image, active, administrator, email, name, middle_name, last_name,
                        position, current_user)


@router.put('/{u_id}', response_model=schemas.UserDisplay, status_code=200)
def update_user(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user),
                request: schemas.UserUpdateBase = Depends()):
    return users.update_user(db, id, current_user.administrator, request)


# handler delete user
# @router.delete('/{u_id}', response_model=schemas.UserDisplay)
# def delete_user(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
#
#     return users.delete(db, id, current_user.administrator)
@router.delete('/{u_id}', status_code=status.HTTP_200_OK)
def delete_user(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    users.delete(db, id, current_user.administrator)
    return {'message': f'User with id {id} have been deleted successfully!'}


# no authentication required
@router.get("/test", response_model=list[schemas.UserDisplay])
def get_users(db: Session = Depends(get_db)):
    return users.get_all(db)

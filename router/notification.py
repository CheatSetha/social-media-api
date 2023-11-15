from fastapi import APIRouter, Depends, status
from schemas import NotificationBase, NotificationDisplay
from sqlalchemy.orm.session import Session
from database import get_db

from typing import List, Optional
from controller import notification
from auth.oauth2 import get_current_user

router = APIRouter(
    prefix='/notification',
    tags=['notification']
)


@router.post('/', response_model=Optional[NotificationDisplay])
def create(request: NotificationBase, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return notification.create(db, request, current_user)


# @router.get('/all/', response_model=List[NotificationDisplay])
# def posts(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
#    return db_post.get_all(db, current_user)


# ID is USER_ID - get all notifications of one user
@router.get('/{email}', response_model=List[
    NotificationDisplay])  # , response_model = NotificationDisplay
def post(email: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return notification.get_all_from_user(db, email, current_user)


# ID is USER_ID
@router.post('/update/{id}', response_model=List[NotificationDisplay])
def update_container(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return notification.update_notification(db, id, current_user)

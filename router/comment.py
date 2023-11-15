from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session
from database import get_db
from controller import commnet
from auth.oauth2 import get_current_user
from schemas import CommentBase, UserAuth, InsertComment

router = APIRouter(
    prefix='/comment',
    tags=['comment']
)


@router.get('/all/{post_id}')
def comments(post_id: int, db: Session = Depends(get_db)):
    return commnet.get_all(db, post_id)


@router.post('')
def create(request: InsertComment, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return commnet.create(db, request, current_user)


@router.post('/delete/{id}')
def delete(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return commnet.delete(db, id, current_user)

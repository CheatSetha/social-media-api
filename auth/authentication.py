from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session
from database import get_db
from models import DbUser
from utils.hashing import Hash
from auth.oauth2 import create_access_token, get_current_user , create_refresh_token
from typing import Annotated, Union

router = APIRouter(
    prefix='/auth',
    tags=['authentication']
)


@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(DbUser).filter(DbUser.email == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Invalid credentials')
    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Incorrect password')

    access_token = create_access_token(data={'email': user.email})
    refresh_token = create_refresh_token(data={'email': user.email})

    return {
        'token_type': 'bearer',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'name': user.name,
            'last_name': user.last_name,
            'user_id': user.id,
            'email': user.email,
            'image_url': user.image_url,
            'administrator': user.administrator
        }
    }


@router.get("/users/me")
async def read_users_me(
        current_user: Annotated[DbUser, Depends(get_current_user)]
):
    return current_user

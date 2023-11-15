from fastapi import HTTPException, status, UploadFile , Form
import datetime
from typing import List
import os
from sqlalchemy.orm.session import Session

import schemas
from models import DbUser
from utils.hashing import Hash
from utils.fileutils import validate_file_size, validate_file_extension


# Event function to create a new user if none exist
def create_initial_user(db: Session):
    user = db.query(DbUser).first()

    if user is None:
        new_user = DbUser(
            email='setha@gmail.com',
            password=Hash.bcrypt('setha123'),
            administrator=True,
            name='bong setha',
            middle_name='zin',
            last_name='2',
            date_of_birth='25/10/2001',
            position='WebDeveloper',
            active=True,
            image_url='https://static.wikia.nocookie.net/onepiece/images/e/e6/Tony_Tony_Chopper_Anime_Pre_Timeskip_Infobox.png/revision/latest?cb=20230906213030',
            created_at=datetime.datetime.now(),
            last_modify=datetime.datetime.now(),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)


def create(
        db: Session, password: str, date_of_birth: datetime, image: UploadFile,
        active: bool, administrator: bool, email: str, name: str, middle_name: str,
        last_name: str, position: str, current_user: DbUser
):
    if not current_user.administrator:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to create a new user',
        )
    user_exist = db.query(DbUser).filter(DbUser.email == email).first()
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User already exist',
        )
    image_dir = f"images/users/"
    os.makedirs(image_dir, exist_ok=True)

    imageListAsString = " "
    validate_file_extension(os.path.splitext(image.filename)[1])
    validate_file_size(image.file, 5 * 1024 * 1024)

    file_extension = os.path.splitext(image.filename)[1]
    new_filename = f"{email}{file_extension}"

    file_patch = os.path.join(image_dir, new_filename)
    with open(file_patch, 'wb+') as file:
        file.write(image.file.read())

    new_user = DbUser(
        email=email,
        password=Hash.bcrypt(password),
        administrator=administrator,
        name=name,
        middle_name=middle_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        position=position,
        image_url=file_patch,
        active=active,
        created_at=datetime.datetime.now(),
        last_modify=datetime.datetime.now(),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_user(db: Session, id: int, current_user: bool, request: schemas.UserUpdateBase):
    user = db.query(DbUser).filter(DbUser.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User id {id} not found!")

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User don't have authorization!")

    user.email = request.email
    user.password = Hash.bcrypt(request.password)
    user.administrator = request.administrator
    user.name = request.name
    user.middle_name = request.middle_name
    user.last_name = request.last_name
    user.date_of_birth = request.date_of_birth
    user.position = request.position
    user.active = request.active
    user.image_url = request.image_url
    user.last_modify = datetime.datetime.now()

    user_exist = db.query(DbUser).filter(DbUser.email == request.email).first()
    if user_exist and user_exist.id != user.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Inserted email already exist!")

    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str):
    user = db.query(DbUser).filter(DbUser.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with email {email} not found')
    return user


def get_user_by_id(db: Session, id: str, current_user: DbUser):
    if (not current_user.administrator and not current_user.id == id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User don't have authorization!")

    user = db.query(DbUser).filter(DbUser.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with id {id} not found')
    return user


def get_all(db: Session):
    return db.query(DbUser).all()


def get_all_users(db: Session, current_user_admin: bool, skip: int = 0, limit: int = 20):
    if (not current_user_admin):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User don't have authorization!")

    # return db.query(DbUser).all()
    return db.query(DbUser).offset(skip).limit(limit).all()


def delete(db: Session, id: int, current_user_admin: bool):
    user = db.query(DbUser).filter(DbUser.id == id).first()

    if not current_user_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User don't have authorization!")
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id {id} not found")

    db.delete(user)
    db.commit()
    deleted_msg = f'user with id {id} deleted successfully!'
    return user

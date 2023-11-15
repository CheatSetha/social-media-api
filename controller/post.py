import math
import shutil
from typing import List
from fastapi import UploadFile, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import current_user

import schemas
from models import DbUser, DbPost, DbContainer
import datetime
from utils.fileutils import validate_file_size, validate_file_extension
from schemas import PostBase, PostInsert, PostDisplay
import os


def create(db: Session, images: List[UploadFile], reference_number: str, description: str, current_user: DbUser):
    # container_exist is a variable to check if the container exist in the database
    container_exist = db.query(DbContainer).filter(DbContainer.reference_number == reference_number).first()
    if container_exist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='inserted container reference number does not exist!'
        )
    post_exist = db.query(DbPost).filter(DbPost.reference_number == reference_number).first()
    if post_exist is not None and container_exist.reference_number == post_exist.reference_number:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Post for this container reference already exist")
    if container_exist.responsible_email != current_user.email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You are not authorized to create a new post for this container")
    image_dir = f"images/posts/{reference_number}"
    os.makedirs(image_dir, exist_ok=True)

    imageListAsString = " "
    for image in images:
        validate_file_extension(os.path.splitext(image.filename)[1])
        validate_file_size(image.file, 5 * 1024 * 1024)

        imageListAsString += f"{image.filename} "
        file_extension = os.path.splitext(image.filename)[1]
        new_filename = f"{image.filename}"

        file_patch = os.path.join(image_dir, new_filename)
        with open(file_patch, 'wb+') as file:
            file.write(image.file.read())

        new_post = DbPost(
            image_url=imageListAsString,
            description=description,
            user_id=current_user.id,
            created_at=datetime.datetime.now(),
            last_modify=datetime.datetime.now(),
            reference_number=reference_number,
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post


def get_all(db: Session, current_user: DbUser):
    if not current_user.administrator:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to get all posts'
        )
    return db.query(DbPost).all()


def get_all_package(db: Session, current_user: DbUser, user_id=None, page: int = 1, per_page: int = 10):
    offset = (page - 1) * per_page

    #     if admin
    if current_user.administrator:
        query = db.query(DbPost)
        if user_id:
            query = query.filter(DbPost.user_id == user_id)
        total_line = query.count()
        query = query.order_by(DbPost.last_modify.desc()).offset(offset).limit(per_page).all()
        total_page = math.ceil(total_line / per_page)  # calculate total page
        return {
            'lines': total_line,
            'total_number_of_pages': total_page,
            'lines_per_page': per_page,
            'actual_page': page,
            'data': query
        }

    if not current_user.administrator:
        query = db.query(DbPost).filter(DbPost.user_id == current_user.id)
        total_line = query.count()
        query = query.order_by(DbPost.last_modify.desc()).offset(offset).limit(per_page).all()
        total_page = math.ceil(total_line / per_page)
        return {
            'lines': total_line,
            'total_number_of_pages': total_page,
            'lines_per_page': per_page,
            'actual_page': page,
            'data': query
        }


def get_by_id(db: Session, id: int, current_user: DbUser):
    post = db.query(DbPost).filter(DbPost.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post with id {id} not found'
        )
    if not current_user.administrator and current_user.id != post.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to get this post'
        )
    return post


def update(db: Session, id: int, current_user: DbUser, request: schemas.PostInsert):
    post = db.query(DbPost).filter(DbPost.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post with id {id} not found'
        )
    if not current_user.administrator and current_user.id != post.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to update this post'
        )
    post.description = request.description
    post.last_modify = datetime.datetime.now()
    post.image_url = request.image_url
    post.reference_number = request.reference_number

    db.commit()
    db.refresh(post)
    return post


def delete(db: Session, id: int, current_user: DbUser):
    post = db.query(DbPost).filter(DbPost.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post with id {id} not found'
        )
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not authorized to delete this post'
        )
    db.delete(post)
    db.commit()
    return {'message': f'Post with id {id} have been deleted successfully!'}

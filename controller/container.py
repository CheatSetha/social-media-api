from schemas import ContainerBase
from sqlalchemy.orm import Session
from models import DbContainer, DbUser
from fastapi import status, HTTPException
import datetime


def create(
        db: Session,
        country: str,
        transport_type: str,
        product_type: str,
        reference_number: str,
        location: str,
        responsible_name: str,
        responsible_email: str,
        client_name: str,
        current_user: DbUser
):
    # VALIDATE THAT USER HAS AUTH TO MAKE CONTAINER
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User don't have authorization!")

    # VALIDATE THAT CONTAINER DOESNT EXIST ALREADY
    container_exist = db.query(DbContainer).filter(DbContainer.reference_number == reference_number).first()
    if container_exist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Inserted container reference number already exist!")

    # VALIDATE EMAIL
    email = responsible_email
    # Check if email exists in the user table
    if db.query(DbUser).filter(DbUser.email == email).first() is None and email is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid responsible email: {email}. User does not exist.")

    new_container = DbContainer(
        reference_number=reference_number,
        location=location,
        country=country,
        responsible_name=responsible_name,
        responsible_email=responsible_email,
        client_name=client_name,
        transport_type=transport_type,
        product_type=product_type,
        created_at=datetime.datetime.now(),
        last_modify=datetime.datetime.now(),
    )
    db.add(new_container)
    db.commit()
    db.refresh(new_container)
    return new_container


def update_container(db: Session, id: int, current_user: bool, request: ContainerBase):
    container = db.query(DbContainer).filter(DbContainer.id == id).first()

    if not container:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Container id {id} not found!")

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User don't have authorization!")

    container.reference_number = request.reference_number
    container.location = request.location
    container.country = request.country
    container.responsible_name = request.responsible_name
    container.responsible_email = request.responsible_email
    container.client_name = request.client_name
    container.transport_type = request.transport_type
    container.product_type = request.product_type
    container.last_modify = datetime.datetime.now()

    container_exist = db.query(DbContainer).filter(DbContainer.reference_number == request.reference_number).first()
    if container_exist and container_exist.id != container.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Inserted email already exist!")

    db.commit()
    db.refresh(container)
    return container


def get_container_by_reference_number(db: Session, reference_number: str, current_user: DbUser):
    # print(reference_number)
    container = db.query(DbContainer).filter(DbContainer.reference_number == reference_number).first()

    if (not current_user.administrator and not current_user.email == container.responsible_email):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User don't have authorization!")

    if not container:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Container with reference_number {reference_number} not found')
    return container


def get_container_by_id(db: Session, id: str, current_user: DbContainer):
    if (not current_user.administrator and not current_user.id == id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User don't have authorization!")

    container = db.query(DbContainer).filter(DbContainer.id == id).first()

    if not container:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Container with id {id} not found')
    return container


def get_all_containers(db: Session, current_user_admin: bool):
    if (not current_user_admin):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User don't have authorization!")

    return db.query(DbContainer).all()


def delete(db: Session, id: int, current_user_admin: bool):
    container = db.query(DbContainer).filter(DbContainer.id == id).first()
    if not current_user_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User don't have authorization!")
    if not container:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Container with id {id} not found")
    db.delete(container)
    db.commit()
    return container

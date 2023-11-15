from sqlalchemy.orm.session import Session
from database import get_db
from fastapi import APIRouter, Depends, Form
from schemas import ContainerDisplay, ContainerBase
from controller import container
from auth.oauth2 import get_current_user
from typing import Optional, List

router = APIRouter(
    prefix="/containers",
    tags=["container"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.post('/', response_model=ContainerDisplay)
def create_container(req: ContainerBase, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return container.create(db, current_user.administrator, req)


@router.post("/create")
def submit_form(
        country: str = Form(...),
        transport_type: str = Form(...),
        product_type: str = Form(...),
        reference_number: str = Form(...),
        location: Optional[str] = Form(None),
        responsible_name: str = Form(...),
        responsible_email: str = Form(...),
        client_name: str = Form(...),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    return container.create(db, country, transport_type, product_type, reference_number, location, responsible_name,
                            responsible_email, client_name, current_user)


@router.get('/all', response_model=List[ContainerDisplay])
def get_all_containers(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return container.get_all_containers(db, current_user.administrator)


@router.get('/{id}', response_model=ContainerDisplay)
def get_container(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return container.get_container_by_id(db, id, current_user)


@router.get('/reference/{reference_number}', response_model=ContainerDisplay)
def get_container(reference_number: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return container.get_container_by_reference_number(db, reference_number, current_user)


@router.post('/update/{id}', response_model=ContainerDisplay)
def update_container(id: int, request: ContainerBase, db: Session = Depends(get_db),
                     current_user=Depends(get_current_user)):
    return container.update_container(db, id, current_user.administrator, request)


@router.post('/delete/{id}')
def delete(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return container.delete(db, id, current_user.administrator)

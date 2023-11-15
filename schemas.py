from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


#############*** USER ***##################
class UserBase(BaseModel):
    email: str
    password: str
    administrator: bool
    name: str
    middle_name: str
    last_name: str
    date_of_birth: str
    position: str
    image_url: str
    active: bool
    created_at: Optional[datetime] = None
    last_modify: Optional[datetime] = None


class UserUpdateBase(BaseModel):
    email: str
    password: str
    administrator: bool
    name: str
    middle_name: str
    last_name: str
    date_of_birth: str
    position: str
    active: bool
    image_url: str
    # last_modify: datetime

    class Config():
        orm_mode = True


class UserDisplay(BaseModel):
    id: int
    email: str
    administrator: bool
    name: str
    middle_name: Optional[str] = None
    last_name: str
    date_of_birth: str
    position: str
    active: bool
    image_url: str
    created_at: datetime
    last_modify: datetime

    class Config():
        orm_mode = True


###########################################
###########*** CONTAINER ***###############
class ContainerBase(BaseModel):
    reference_number: str
    location: Optional[str] = None
    country: str
    responsible_name: str
    responsible_email: Optional[str]
    client_name: str
    transport_type: str
    product_type: str
    created_at: Optional[datetime] = None
    last_modify: Optional[datetime] = None


# For ContainerDisplay
class ContainerDisplay(BaseModel):
    id: int
    reference_number: str
    location: Optional[str] = None
    country: str
    responsible_name: str
    responsible_email: Optional[str]
    client_name: str
    transport_type: str
    product_type: str
    created_at: datetime
    last_modify: datetime

    class Config():
        orm_mode = True


###########################################
#############*** POST ***##################
class PostBase(BaseModel):
    image_url: str
    description: str
    user_id: int
    created_at: datetime
    last_modify: datetime
    reference_number: str


# # InsertPost - Napravi ovo kad zarvsis. ideja je da pri unosu
class PostInsert(BaseModel):
    image_url: str
    description: str
    reference_number: str


# For PostDisplay
class User(BaseModel):
    email: str
    name: str
    last_name: str
    id: int
    image_url: str

    class Config():
        orm_mode = True


# For PostDisplay
class Comment(BaseModel):
    id: int
    text: str
    name: str
    last_name: str
    email: str
    created_at: datetime
    last_modify: datetime

    class Config():
        orm_mode = True


class PostDisplay(BaseModel):
    id: int
    image_url: str
    description: str
    created_at: datetime
    last_modify: datetime
    reference_number: str
    user: User
    comments: List[Comment]
    container: ContainerDisplay

    class Config():
        orm_mode = True


class PackageResponse(BaseModel):
    lines: int
    total_number_of_pages: int
    lines_per_page: int
    actual_page: int
    data: List[PostDisplay]


# NEZNAM STO CE MI TO
class UserAuth(BaseModel):
    id: int
    email: str

    class Config():
        orm_mode = True


###########################################
###########*** COMMENT ***#################

class CommentBase(BaseModel):
    name: str
    last_name: str
    email: str
    text: str
    created_at: datetime
    last_modify: datetime
    post_id: int


# # InsertComment
class InsertComment(BaseModel):
    text: str
    post_id: int
    post_owner_email: str


###########################################
########*** NOTIFICATIONS ***##############

class NotificationBase(BaseModel):
    comment_owner_id: int
    # comment_owner_name: str
    # comment_owner_last_name: str
    # comment_owner_image : str
    notification_owner_email: str
    post_owner_email: str
    post_id: int
    comment_time: datetime
    is_read: bool
    message: str


class NotificationDisplay(BaseModel):
    id: int
    comment_owner_id: int
    comment_owner_name: str
    comment_owner_last_name: str
    comment_owner_image: str
    notification_owner_email: str
    post_owner_email: str
    post_id: int
    comment_time: datetime
    is_read: bool
    message: str
    owner: User
    post: PostDisplay

    class Config():
        orm_mode = True

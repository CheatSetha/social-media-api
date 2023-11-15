from database import Base
from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import Integer, String, DateTime, Boolean
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship

from sqlalchemy import event


class DbUser(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    password = Column(String)
    email = Column(String, unique=True)
    administrator = Column(Boolean)
    name = Column(String)
    middle_name = Column(String)
    last_name = Column(String)
    date_of_birth = Column(String)
    position = Column(String)
    image_url = Column(String)
    active = Column(Boolean)
    created_at = Column(DateTime)
    last_modify = Column(DateTime)
    items = relationship('DbPost', back_populates='user')
    container = relationship('DbContainer', back_populates='user')
    comments = relationship("DbComment", back_populates='user')
    notifications = relationship(
        "DbNotifications",
        back_populates='owner',
        foreign_keys='DbNotifications.notification_owner_email',
        cascade='all, delete-orphan'
    )


class DbContainer(Base):
    __tablename__ = 'container'
    id = Column(Integer, primary_key=True, index=True)
    reference_number = Column(String, nullable=False, unique=True)
    location = Column(String)
    country = Column(String)
    responsible_name = Column(String)
    responsible_email = Column(String, ForeignKey("user.email"))
    client_name = Column(String)
    transport_type = Column(String)
    product_type = Column(String)
    created_at = Column(DateTime)
    last_modify = Column(DateTime)
    user = relationship('DbUser', back_populates='container')
    posts = relationship('DbPost', back_populates='container')


@event.listens_for(DbUser, 'before_delete')
def nullify_responsible_email(mapper, connection, target):
    connection.execute(
        DbContainer.__table__.update().
        where(DbContainer.responsible_email == target.email).
        values(responsible_email=None)
    )


class DbPost(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String)
    description = Column(String)
    created_at = Column(DateTime)
    last_modify = Column(DateTime)
    reference_number = Column(String, ForeignKey('container.reference_number'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('DbUser', back_populates='items')
    comments = relationship('DbComment', back_populates='post')
    container = relationship('DbContainer', back_populates='posts')
    notifications = relationship("DbNotifications", back_populates='post')


class DbComment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))
    created_at = Column(DateTime)
    email = Column(String)
    last_modify = Column(DateTime)
    post_id = Column(Integer, ForeignKey('post.id'))
    post = relationship("DbPost", back_populates='comments')
    user = relationship("DbUser", back_populates='comments')


class DbNotifications(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True, index=True)
    notification_owner_email = Column(String, ForeignKey('user.email'))
    post_owner_email = Column(String, ForeignKey('user.email'))
    post_id = Column(Integer, ForeignKey('post.id'))
    comment_time = Column(DateTime)
    is_read = Column(Boolean, default=False)
    message = Column(String)
    owner = relationship(
        "DbUser",
        back_populates='notifications',
        foreign_keys='DbNotifications.notification_owner_email'
    )
    post = relationship("DbPost", back_populates='notifications')

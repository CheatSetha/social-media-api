from schemas import NotificationBase , NotificationDisplay
from sqlalchemy.orm.session import Session
from models import DbNotifications, DbUser , DbComment
import datetime
from fastapi import HTTPException, status
from sqlalchemy import and_, func , delete


def create(db: Session, request, current_user: DbUser):
    # Extract all who comment this post
    results = (
        db.query(DbComment.email)
        .filter(DbComment.post_id == request.post_id)
        .distinct()
        .all()
    )

    # Extract the emails from the result
    emails = [row[0] for row in results]

    # Iterate over each email and if some of email is not current user prepare notification for them/it
    for email in emails:
        if email != current_user.email:
            new_notification = DbNotifications(
                notification_owner_email=email,
                comment_owner_id=current_user.id,
                post_owner_email=request.post_owner_email,
                post_id=request.post_id,
                comment_time=datetime.datetime.now(),
                message=request.text,
            )
            db.add(new_notification)
            db.commit()
            db.refresh(new_notification)

        # if emails which comment for this post exist and not post owner
        if email == current_user.email and current_user.email != request.post_owner_email:
            new_notification = DbNotifications(
                notification_owner_email=request.post_owner_email,
                comment_owner_id=current_user.id,
                # comment_owner_name=current_user.name,
                # comment_owner_last_name=current_user.last_name,
                post_owner_email=request.post_owner_email,
                post_id=request.post_id,
                comment_time=datetime.datetime.now(),
                message=request.text,
            )
            db.add(new_notification)
            db.commit()
            db.refresh(new_notification)


def get_all_from_user(db: Session, email: str, current_user: DbUser):
    user_notifications = db.query(DbNotifications).filter(DbNotifications.notification_owner_email == email). \
        order_by(DbNotifications.comment_time.desc()).all()

    if not user_notifications:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Notification from user {email} not found!")

    if current_user.email != email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"User don't have authorization!")

    # user_maker = db.query(DbUser).filter(DbUser.id == user_notifications[0].comment_owner_id).first()

    # additional_fields = {
    # 'comment_owner_name': user_maker.name,
    # 'comment_owner_last_name': user_maker.last_name,
    # 'comment_owner_image': user_maker.image_url
    # }

    # user_notifications = {**user_notifications, **additional_fields}
    for notification in user_notifications:
        user_maker = db.query(DbUser).filter(DbUser.id == notification.comment_owner_id).first()

        additional_fields = {
            'comment_owner_name': user_maker.name,
            'comment_owner_last_name': user_maker.last_name,
            'comment_owner_image': user_maker.image_url
        }

        notification.__dict__.update(additional_fields)

    return user_notifications


def update_notification(db: Session, id: int, current_user: DbUser):
    notification = db.query(DbNotifications).filter(DbNotifications.id == id).first()
    # notification = (
    # db.query(DbNotifications, DbUser.email)
    # .join(DbUser, DbNotifications.comment_owner_id == DbUser.id)
    # .filter(DbNotifications.id == id)
    # .first()
    # )

    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Notification id {id} not found!")

    post_id = notification.post_id
    post_owner_email = notification.post_owner_email

    # Set is_read=True for notifications with the same post_id and post_owner_email
    db.query(DbNotifications).filter(
        DbNotifications.post_id == post_id,
        DbNotifications.post_owner_email == post_owner_email,
        DbNotifications.notification_owner_email == current_user.email
    ).update({DbNotifications.is_read: True})

    db.commit()

    # Count unread notifications for the current user
    unread_count = db.query(DbNotifications).filter(
        DbNotifications.is_read == False,
        DbNotifications.notification_owner_email == current_user.email
    ).count()

    # Delete excess notifications for current user
    if unread_count >= 5:
        delete_query = delete(DbNotifications).where(
            and_(
                DbNotifications.is_read == True,
                DbNotifications.notification_owner_email == current_user.email
            )
        )
    else:
        preserved_count = 5 - unread_count
        delete_query = delete(DbNotifications).where(
            and_(
                DbNotifications.is_read == True,
                DbNotifications.notification_owner_email == current_user.email,
                ~DbNotifications.id.in_(
                    db.query(DbNotifications.id).filter(
                        DbNotifications.notification_owner_email == current_user.email
                    ).order_by(DbNotifications.id.desc()).limit(preserved_count)
                )
            )
        )
    db.execute(delete_query)
    db.commit()

    db.refresh(notification)
    return get_all_from_user(db, current_user.email, current_user)

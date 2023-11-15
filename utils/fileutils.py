import os
from fastapi import HTTPException, status, UploadFile
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def validate_file_extension(file_extension: str):
    allowed_extensions = [".jpg", ".jpeg", ".png"]
    if not file_extension.lower() in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file extension. Allowed extensions: .jpg, .jpeg, .png",
        )


def validate_file_size(file: UploadFile, max_size: int):
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds the maximum limit of {max_size} bytes",
        )

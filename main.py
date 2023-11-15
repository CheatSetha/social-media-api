from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from router import user,post, container, comment , notification
from auth import authentication
from database import engine
import models

app = FastAPI()
app.include_router(user.router)
app.include_router(authentication.router)
app.include_router(post.router)
app.include_router(container.router)
app.include_router(comment.router)
app.include_router(notification.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # origins,
    allow_credentials=True,

    allow_methods=['*'],
    allow_headers=['*']
)

# create tables in database
models.Base.metadata.create_all(bind=engine)

app.mount('/images', StaticFiles(directory='images'), name='images')

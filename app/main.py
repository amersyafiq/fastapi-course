from random import randrange
from fastapi import FastAPI

from . import models
from .database import engine
from .routers import post, user, auth, vote
from .config import settings

import subprocess
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

# models.Base.metadata.create_all(bind=engine)

origins = ['*']

app = FastAPI()

@app.on_event("startup")
async def run_migrations():
    subprocess.run(["alembic", "upgrade", "head"], check=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], #allow specific http methods (like post request, only get)
    allow_headers=["*"],
)
        
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

#    http method
@app.get("/") # path operation
async def root():
    return {"message": "Welcome to my APIs"}
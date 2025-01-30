from fastapi import APIRouter, HTTPException, Depends, File, Form
from sqlalchemy.orm import Session
from models import User, get_db, DB_Session_Maker, Upload
import logging
from pydantic import BaseModel
from datetime import date
from fastapi_login import LoginManager
import os
from time import sleep
from datetime import timedelta, datetime

from models import get_db
import utils.password_utils as password_utils

log = logging.getLogger(__name__)

router = APIRouter()

SECRET = "8aa279dce3396185" # TODO: move to .secret file
login_manager = LoginManager(SECRET, token_url="/login")

class UserLoginConstruct(BaseModel):
    email: str
    password: str

class NewUserConstruct(BaseModel):
    email: str
    username: str
    password: str

@login_manager.user_loader()
def load_user(email: str):
    db = DB_Session_Maker()
    user = db.query(User).filter(User.email == email).first()
    db.close()
    return user

@router.get("/")
async def home():
    return ":)"

@router.post("/user", status_code=201)
async def add_user(user: NewUserConstruct, db: Session = Depends(get_db)):

    if db.query(User).filter(User.email == user.email).first():
        log.info(f'User with email {user.email} already exists.')
        raise HTTPException(status_code=409, detail=f'User with email {user.email} already exists.')
    
    if db.query(User).filter(User.username == user.username).first():
        log.info(f'User with username {user.username} already exists.')
        raise HTTPException(status_code=409, detail=f'User with username {user.username} already exists.')
    
    password_hash = password_utils.hash_password(user.password)
    new_user = User(email=user.email, password_hash=password_hash, username=user.username)

    db.add(new_user)
    db.commit()
    log.info(f"Created new user {new_user}")

    return {"message": "User created successfully"}


@router.post("/login")
async def login(user: UserLoginConstruct, db: Session = Depends(get_db)):
    email = user.email
    password = user.password

    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        log.info(f'User with email {email} not found.')
        raise HTTPException(status_code=404, detail="User not found")

    if not password_utils.check_password(password, db_user.password_hash):
        log.info(f'Invalid password for user {email}.')
        raise HTTPException(status_code=401, detail="Invalid password")
    
    access_token = login_manager.create_access_token(data={"sub": email}, expires=timedelta(days=1))
    return {"access_token": access_token, "token_type": "bearer"}

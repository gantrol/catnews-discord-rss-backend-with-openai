from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app import schemas, crud, token
from app.api import deps
from app.utils.auth import authenticate_user

router = APIRouter()


# token instead of user?
@router.post("/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(deps.get_db)):
    if crud.user.get_user_by_email(db=db, email=user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    if crud.user.get_user_by_username(db=db, username=user.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    created_user = crud.user.create_user(db=db, user=user)
    access_token = token.create_access_token(subject=created_user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=schemas.Token)
def login(user_login: schemas.UserLogin = Body(...), db: Session = Depends(deps.get_db)):
    user = crud.user.get_user_by_email(db=db, email=user_login.email)
    if not user or not authenticate_user(db, user.username, user_login.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = token.create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}

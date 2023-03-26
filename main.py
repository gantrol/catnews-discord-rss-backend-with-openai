import os
import secrets
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from requests_oauthlib import OAuth2Session
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app import crud, models, schemas
from app.crud import authenticate_user
from app.database import create_access_token, get_db, engine, get_current_user
from app.schemas import UserCreate, Token

SCOPE = ["identify", "email", "guilds.join", "guilds.members.read"]

load_dotenv()
models.Base.metadata.create_all(bind=engine)
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# TODO: 认证邮箱……
# Registration and authentication endpoints
@app.post("/auth/register", status_code=status.HTTP_201_CREATED, response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(user.email, db)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.register_user(user, db)
    access_token = create_access_token(data={"sub": user.email}, token_source="Password")
    return {"access_token": access_token, "token_type": "bearer", "token_source": "Password"}


# TODO: 没有密码（其他OAuth2途径来的）……
@app.post("/auth/token", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db),
):
    """

    :param form_data: form_data.username is email...
    :param db:
    :return:
    """
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email}, token_source="Password")
    return {"access_token": access_token, "token_type": "bearer", "token_source": "Password"}


# Discord OAuth2
@app.get("/auth/discord")
async def auth_discord():
    state = secrets.token_hex(16)
    discord = OAuth2Session(
        os.getenv("CLIENT_ID_DISCORD"),
        redirect_uri=os.getenv("REDIRECT_URI_DISCORD"),
        scope=SCOPE,
        state=state,
    )
    authorization_url, _ = discord.authorization_url("https://discord.com/api/oauth2/authorize")
    #     return {"url": authorization_url}
    return RedirectResponse(authorization_url)


@app.get("/auth/discord/callback")
async def auth_discord_callback(code: str, state: str, db: Session = Depends(get_db)):
    discord = OAuth2Session(
        os.getenv("CLIENT_ID_DISCORD"),
        redirect_uri=os.getenv("REDIRECT_URI_DISCORD"),
        scope=SCOPE,
        state=state,
    )
    token = discord.fetch_token(
        "https://discord.com/api/oauth2/token",
        client_secret=os.getenv("CLIENT_SECRET_DISCORD"),
        code=code,
        include_client_id=True,
    )

    user_data = discord.get("https://discord.com/api/users/@me").json()

    user = crud.get_user_by_discord_id(user_data["id"], db)
    if not user:
        user = crud.create_user_with_discord(user_data, token, db)
    else:
        crud.update_discord_token(user.id, token, db)
    return {"user_data": user_data, "token": token}


# GitHub OAuth2
@app.get("/auth/github")
async def auth_github():
    github = OAuth2Session(
        os.getenv("CLIENT_ID_GITHUB"),
        redirect_uri=os.getenv("REDIRECT_URI_GITHUB"),
        scope=["user:email"],
    )
    authorization_url, _ = github.authorization_url("https://github.com/login/oauth/authorize")
    return {"url": authorization_url}


@app.get("/auth/github/callback")
async def auth_github_callback(code: str):
    github = OAuth2Session(
        os.getenv("CLIENT_ID_GITHUB"),
        redirect_uri=os.getenv("REDIRECT_URI_GITHUB"),
        scope=["user:email"],
    )
    token = github.fetch_token(
        "https://github.com/login/oauth/access_token",
        client_secret=os.getenv("CLIENT_SECRET_GITHUB"),
        code=code,
    )
    user_data = github.get("https://api.github.com/user").json()
    return {"user_data": user_data, "token": token}


@app.post("/feeds", status_code=status.HTTP_201_CREATED)
async def add_subscription(feed: schemas.FeedCreate, current_user: models.User = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    subscribed_feed = crud.subscribe_to_feed(feed, current_user, db)
    return subscribed_feed


@app.post("/feeds/unsubscribe", status_code=status.HTTP_200_OK)
async def remove_subscription(feed: schemas.FeedRemove, current_user: models.User = Depends(get_current_user),
                              db: Session = Depends(get_db)):
    unsubscribed_feed = crud.unsubscribe_from_feed(feed, current_user, db)
    if unsubscribed_feed:
        return unsubscribed_feed
    else:
        raise HTTPException(status_code=404, detail="Feed not found")


@app.get("/feeds", response_model=List[schemas.Feed])
async def list_subscriptions(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    subscribed_feeds = crud.list_subscribed_feeds(current_user, db)
    return subscribed_feeds


@app.get("/articles", response_model=List[schemas.Article])
async def get_feed_articles(
        skip: int = 0, limit: int = 20, current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    articles = crud.get_feed_articles(current_user, db, skip=skip, limit=limit)
    return articles


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

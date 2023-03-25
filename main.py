from datetime import timedelta
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas, database

from app.models import OAuth2Provider

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(database.get_db)):
    user = database.authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=database.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = database.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/feeds/", response_model=schemas.Feed)
def subscribe_to_feed(feed: schemas.FeedCreate, db: Session = Depends(database.get_db),
                      current_user: models.User = Depends(database.get_current_user)):
    return crud.subscribe_to_feed(db=db, feed=feed, user=current_user)


@app.post("/feeds/unsubscribe", response_model=schemas.Feed)
def unsubscribe_from_feed(feed: schemas.FeedCreate, db: Session = Depends(database.get_db),
                          current_user: models.User = Depends(database.get_current_user)):
    return crud.unsubscribe_from_feed(db=db, feed=feed, user=current_user)


@app.get("/feeds/subscribed", response_model=List[schemas.Feed])
def list_subscribed_feeds(db: Session = Depends(database.get_db),
                          current_user: models.User = Depends(database.get_current_user)):
    return crud.list_subscribed_feeds(db=db, user=current_user)


@app.get("/feeds/", response_model=List[schemas.Article])
def get_feed_articles(db: Session = Depends(database.get_db),
                      current_user: models.User = Depends(database.get_current_user)):
    return crud.get_feed_articles(db=db, user=current_user)


@app.post("/auth/discord")
async def discord_oauth2(token: str, db: Session = Depends(database.get_db), user=Depends(
    database.get_current_user)):
    # Validate the access token and get the user's Discord information
    discord_user_info = await get_discord_user_info(token)

    if not discord_user_info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    # Check if the user already has a Discord account linked
    if user.discord_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Discord account already linked")

    # Link the user's account with their Discord account
    user.discord_id = discord_user_info["id"]

    # Save the OAuth2 access token and refresh token
    oauth2_provider = OAuth2Provider(provider="discord", user_id=user.id, access_token=token,
                                     refresh_token=None, expires_at=None)
    db.add(oauth2_provider)
    db.commit()

    return {"detail": "Discord account linked successfully"}

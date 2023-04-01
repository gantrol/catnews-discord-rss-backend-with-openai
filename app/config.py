from pydantic import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


# if os.environ.get("TESTING"):
#     load_dotenv(".env.test")


class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    OPEN_AI_KEY: str = os.getenv("OPEN_AI_KEY")
    DISCORD_REDIRECT_URL: str = os.getenv("DISCORD_REDIRECT_URL")


settings = Settings()

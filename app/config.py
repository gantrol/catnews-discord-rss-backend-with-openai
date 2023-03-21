from pydantic import BaseSettings


class Settings(BaseSettings):
    # TODO: read from environment
    SECRET_KEY: str = "your_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()

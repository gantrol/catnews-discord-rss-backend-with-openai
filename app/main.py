from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import crud
from app.api import router as api_router
from app.database import SessionLocal

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

from fastapi import APIRouter

from . import feed, article, user, authentication

router = APIRouter()

router.include_router(feed.router, prefix="/feed", tags=["feed"])
router.include_router(article.router, prefix="/article", tags=["article"])
router.include_router(user.router, prefix="/user", tags=["user"])
router.include_router(authentication.router, prefix="/auth", tags=["authentication"])

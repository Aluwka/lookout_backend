from fastapi import APIRouter
from src.api.http.v1.endpoints import auth_html

router = APIRouter()
router.include_router(auth_html.router)

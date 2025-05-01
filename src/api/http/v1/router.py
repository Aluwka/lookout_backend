from fastapi import APIRouter
from .endpoints.auth import router as auth_router
from .endpoints.payment import router as payment_router
from .endpoints.logs import router as logs_router
from .endpoints.video import router as video_router
from .endpoints.analysis_result import router as analysis_result_router
from .endpoints.model import router as model_router
from .endpoints import auth_html

router = APIRouter(prefix="/v1")


router.include_router(auth_router)
router.include_router(payment_router)
router.include_router(logs_router)
router.include_router(video_router)
router.include_router(analysis_result_router)
router.include_router(model_router)
router.include_router(auth_html.router)
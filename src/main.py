from src.core.app.app_creator import app_creator
from src.api.http.api_router import router as api_router

app = app_creator.create_app()
app_creator.add_templates()
app_creator.mount_static()
app_creator.add_router(api_router)

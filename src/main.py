from .core.app.app_creator import app_creator
from fastapi.staticfiles import StaticFiles

app = app_creator.create_app()

app.mount("/", StaticFiles(directory="src/templates", html=True), name="static")

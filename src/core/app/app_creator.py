import os
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List

class AppCreator:
    def __init__(self):
        self._app = FastAPI()
        self.templates = None

    def create_app(self) -> FastAPI:
        return self._app

    def add_router(self, router: APIRouter):
        self._app.include_router(router)

    def add_templates(self, templates_dir: str = "src/templates"):
        self.templates = Jinja2Templates(directory=templates_dir)

    def mount_static(self, static_url: str = "/static", static_dir: str = "src/static"):
        if os.path.isdir(static_dir):
            self._app.mount(static_url, StaticFiles(directory=static_dir), name="static")

app_creator = AppCreator()

from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from src.api.http.api_router import v1_router as api_router



BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

app.include_router(api_router)
# Подключаем статику (CSS, JS, PNG и т.д.)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Указываем папку с шаблонами HTML
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Страница загрузки
@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

# Страница результата для реального видео
@app.get("/result/real", response_class=HTMLResponse)
async def real_result(request: Request):
    return templates.TemplateResponse("real result.html", {"request": request})

# Страница результата для фейкового видео
@app.get("/result/fake", response_class=HTMLResponse)
async def fake_result(request: Request):
    return templates.TemplateResponse("fake result.html", {"request": request})

# Страница профиля (пример)
@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

# Страница профиля (пример)
@app.get("/signin", response_class=HTMLResponse)
async def profile(request: Request):
    return templates.TemplateResponse("signin.html", {"request": request})

# Страница профиля (пример)
@app.get("/login", response_class=HTMLResponse)
async def profile(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

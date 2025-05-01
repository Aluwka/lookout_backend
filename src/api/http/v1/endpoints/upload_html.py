from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/upload", response_class=HTMLResponse)
async def show_upload_page(request: Request):
    from src.core.app.app_creator import app_creator  # 👈 импорт тут
    return app_creator.templates.TemplateResponse("upload.html", {"request": request})


@router.post("/upload", response_class=HTMLResponse)
async def handle_upload(request: Request, file: UploadFile = File(...)):
    from src.core.app.app_creator import app_creator  # 👈 импорт тут
    print(f"[UPLOAD] Received file: {file.filename}")
    return app_creator.templates.TemplateResponse("upload.html", {
        "request": request,
        "filename": file.filename
    })

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from src.schemas.user_schema import UserCreate
from src.usecases.user_usecase import UserUseCase, get_user_use_case

router = APIRouter()


@router.get("/signup")
async def signup_form(request: Request):
    from src.core.app.app_creator import app_creator  # 👈 переместили импорт сюда
    return app_creator.templates.TemplateResponse("signup.html", {"request": request})


@router.post("/signup")
async def signup_submit(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    use_case: UserUseCase = Depends(get_user_use_case)
):
    from src.core.app.app_creator import app_creator  # 👈 и сюда
    try:
        user = UserCreate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )
        await use_case.create_user(user)
        return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
    except Exception as e:
        return app_creator.templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": str(e)}
        )


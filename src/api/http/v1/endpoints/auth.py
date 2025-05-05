from authx import TokenPayload
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from src.schemas.auth_schema import RefreshBody
from src.schemas.user_schema import UserCreate, UserLogin, UserResponse
from src.usecases.user_usecase import UserUseCase, get_user_use_case
from src.api.http.dependencies import security
from src.schemas.responses.auth_response import AuthResponse, RefreshResponse
from src.api.http.exceptions import NotFoundException, BadRequestException, UnauthorizedException, ForbiddenException, InternalServerErrorException


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login(
    user: UserLogin,
    response: Response,
    use_case: UserUseCase = Depends(get_user_use_case),
):
    try:
        user = await use_case.login_user(user=user)
        if not user:
            raise AttributeError("Invalid credentials")
        
        current_user = await use_case.get_user_by_fields(email=user.email)

        access_token = security.create_access_token(
            uid=user.email,
            email=user.email,
            username=current_user.username,
        )

        refresh_token = security.create_refresh_token(
            uid=user.email,
            email=user.email,
            username=current_user.username,
        )

        response.set_cookie(
            key="access_token_cookie",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax"
        )

        response.set_cookie(
            key="refresh_token_cookie",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax"
        )

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    except AttributeError as e:
        raise UnauthorizedException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/register")
async def register(
    user: UserCreate,
    response: Response,
    use_case: UserUseCase = Depends(get_user_use_case),
):
    """
    User registration endpoint.
    """
    try:
        new_user = await use_case.create_user(user)
        if not new_user:
            raise ValueError("User already exists")
        
        access_token = security.create_access_token(
            uid=new_user.email,
            email=new_user.email,
            username=new_user.username,
        )

        refresh_token = security.create_refresh_token(
            uid=new_user.email,
            email=new_user.email,
            username=new_user.username,
        )

        response.set_cookie(
            key="access_token_cookie",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax"
        )
        response.set_cookie(
            key="refresh_token_cookie",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax"
        )

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    except ValueError as e:
        raise BadRequestException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/logout")
async def logout(
    response: Response,
):
    """
    User logout endpoint.
    """
    try:
        response.delete_cookie(key="access_token_cookie")
        response.delete_cookie(key="refresh_token_cookie")
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post('/refresh')
async def refresh(request: Request, response: Response, refresh_data: RefreshBody = None):
    """
    Refresh endpoint - creates a new access token using a refresh token

    Can accept the refresh token either:
    1. In the Authorization header
    2. In the request body as JSON
    """
    try:
        try:
            refresh_payload = await security.refresh_token_required(request)
        except Exception as header_error:
            if not refresh_data or not refresh_data.refresh_token:
                raise header_error

            token = refresh_data.refresh_token
            refresh_payload = security.verify_token(
                token,
                verify_type=True,
                type="refresh"
            )
        access_token = security.create_access_token(refresh_payload.sub)

        response.set_cookie(
            key="access_token_cookie",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax"
        )
        return RefreshResponse(
            access_token=access_token,
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get('/info', response_model=UserResponse)
async def get_user_info(
    user: TokenPayload = Depends(security.access_token_required),
    use_case: UserUseCase = Depends(get_user_use_case),
):
    """
    Get user info endpoint - returns the user info from the access token
    """
    try:
        user_info = await use_case.get_user_by_fields(email=user.sub)
        if not user_info:
            raise HTTPException(status_code=404, detail="User not found")
        return user_info
    except AttributeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
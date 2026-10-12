from fastapi import APIRouter, Depends, status

from schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from services import auth_service
from services.dependencies import get_current_user
from schemas.user import UserInDB

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate):
    """
    Register a new user.
    Returns the created user (no password).
    409 if email already exists.
    """
    return await auth_service.register_user(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin):
    """
    Login with email + password.
    Returns a JWT access token and the user object.
    401 if credentials are wrong.
    """
    user, token = await auth_service.login_user(data.email, data.password)
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            created_at=user.created_at,
            is_active=user.is_active,
        )
    )


@router.get("/me", response_model=UserResponse)
async def me(current_user: UserInDB = Depends(get_current_user)):
    """
    Return the currently authenticated user.
    Requires Bearer token in Authorization header.
    401 if token is missing or invalid.
    """
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        created_at=current_user.created_at,
        is_active=current_user.is_active,
    )
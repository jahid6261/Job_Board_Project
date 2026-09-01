from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.depends.auth_depends import get_current_user
from src.users import services
from src.users.models import UserModel
from src.users.schemas import (
    UserRegistrationRequest,
    UserRegistrationResponse,
    LoginResponse,
    UserLoginRequest,
    UserProfileResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
)
from src.users.services import (
    register,
    activate_account_service,
    login,
    profile,
)
from src.utils.database import get_db

users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.post("/register", response_model=UserRegistrationResponse)
async def users_register(
    request: UserRegistrationRequest,
    db: AsyncSession = Depends(get_db),
):
    return await register(request, db)


@users_router.get("/activate")
async def activate_account(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    return await activate_account_service(token=token, db=db)


@users_router.post("/login", response_model=LoginResponse)
async def user_login(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    return await login(request, db)


@users_router.get("/profile", response_model=UserProfileResponse)
async def user_profile(
    current_user: UserModel = Depends(get_current_user),
):
    return await profile(current_user)


@users_router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    await services.forgot_password(db=db, email=request.email)
    return {"message": "If an account exists with this email, a password reset OTP has been sent."}


@users_router.post("/reset-password", status_code=status.HTTP_200_OK)
async def resets_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    return await services.reset_password(
        db=db,
        email=request.email,
        otp=request.otp,
        new_password=request.new_password,
    )


@users_router.patch("/change-password")
async def user_change_password(
    request: ChangePasswordRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await services.change_password(
        user=current_user,
        current_password=request.current_password,
        new_password=request.new_password,
        confirm_password=request.confirm_password,
        db=db,
    )
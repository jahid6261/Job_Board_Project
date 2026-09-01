from pydantic import BaseModel, EmailStr, Field
from src.users.models import UserRole


class UserRegistrationRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    number: str | None = None
    address: str | None = None


class UserRegistrationResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    number: str | None
    address: str | None
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfileResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    number: str
    address: str
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    first_name: str
    last_name: str
    number: str
    address: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)
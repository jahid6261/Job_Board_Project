from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import (
    UserModel,
    UserRole,
    PasswordResetOTP,

)
from src.users.schemas import (
    UserRegistrationRequest,
    UserLoginRequest,
    LoginResponse,
)

from src.utils.security import (
    hash_password,
    verify_password,
    encode_access_token,
    hash_otp,
)

from src.utils.email import (
    send_activation_email,
    send_password_reset_otp_email,
)

from src.utils.verification_token import (
    generate_verification_token,
    generate_otp,
)


async def register(
    request: UserRegistrationRequest,
    db: AsyncSession,
):
    email = request.email.strip().lower()

    email_query = await db.scalar(
        select(UserModel).where(
            UserModel.email == email
        )
    )

    if email_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )

    number = (
        request.number.strip()
        if request.number
        else None
    )

    if number:
        number_query = await db.scalar(
            select(UserModel).where(
                UserModel.number == number
            )
        )

        if number_query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already exists",
            )

    token = generate_verification_token()

    new_user = UserModel(
        first_name=request.first_name.strip(),
        last_name=request.last_name.strip(),
        email=email,
        password=hash_password(request.password),
        number=number,
        address=(
            request.address.strip()
            if request.address
            else None
        ),
        role=UserRole.job_seeker,
        is_active=False,
        activation_token=token,
    )

    db.add(new_user)

    await db.commit()
    await db.refresh(new_user)

    send_activation_email(
        to_email=new_user.email,
        first_name=new_user.first_name,
        activation_token=token,
    )

    return new_user


async def activate_account_service(
    token: str,
    db: AsyncSession,
):
    result = await db.execute(
        select(UserModel).where(
            UserModel.activation_token == token
        )
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid activation link",
        )

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already activated",
        )

    user.is_active = True
    user.activation_token = None

    await db.commit()
    await db.refresh(user)

    return {
        "message": "Account activated successfully."
    }


async def login(
    request: UserLoginRequest,
    db: AsyncSession,
):
    email = request.email.strip().lower()

    user = await db.scalar(
        select(UserModel).where(
            UserModel.email == email
        )
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before login",
        )

    if not verify_password(
        request.password,
        user.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = encode_access_token(
        user.id,
        user.email,
        user.role.value,
    )

    return LoginResponse(
        access_token=access_token,
    )


async def profile(user: UserModel):
    return user



# FORGOT PASSWORD


async def forgot_password(
    db: AsyncSession,
    email: str,
):
    email = email.strip().lower()

    result = await db.execute(
        select(UserModel).where(
            UserModel.email == email
        )
    )

    user = result.scalar_one_or_none()

    if not user:
        return None

    # Generate OTP
    otp = generate_otp()

    # Hash OTP before storing
    otp_hash = hash_otp(otp)

    # OTP expires in 5 minutes
    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=5)
    )

    reset_otp = PasswordResetOTP(
        user_id=user.id,
        otp=otp_hash,
        expires_at=expires_at,
        is_used=False,
    )

    db.add(reset_otp)

    await db.commit()

    # Send original OTP through email
    send_password_reset_otp_email(
        to_email=user.email,
        first_name=user.first_name,
        otp=otp,
    )

    return {
        "message": "Password reset OTP sent successfully."
    }



# RESET PASSWORD USING OTP


async def reset_password(
    db: AsyncSession,
    email: str,
    otp: str,
    new_password: str,
):
    email = email.strip().lower()

    # Find user
    user = await db.scalar(
        select(UserModel).where(
            UserModel.email == email
        )
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or OTP.",
        )

    # Get latest unused OTP
    result = await db.execute(
        select(PasswordResetOTP)
        .where(
            PasswordResetOTP.user_id == user.id,
            PasswordResetOTP.is_used == False,
        )
        .order_by(
            PasswordResetOTP.created_at.desc()
        )
    )

    reset_otp = result.scalars().first()

    if not reset_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP not found or already used.",
        )

    # Check expiry
    now = datetime.now(timezone.utc)

    expires_at = reset_otp.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    if expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired.",
        )

    # Verify OTP
    if hash_otp(otp) != reset_otp.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or OTP.",
        )

    # Change password
    user.password = hash_password(new_password)

    # OTP can only be used once
    reset_otp.is_used = True

    await db.commit()

    return {
        "message": "Password reset successfully."
    }



async def change_password(
    user: UserModel,
    current_password: str,
    new_password: str,
    confirm_password: str,
    db: AsyncSession,
):
    # Check current password
    if not verify_password(
        current_password,
        user.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    # Check new password and confirm password
    if new_password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirm password do not match.",
        )

    # Prevent using the same password
    if verify_password(
        new_password,
        user.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password.",
        )

    # Hash new password
    user.password = hash_password(new_password)

    await db.commit()
    await db.refresh(user)

    return {
        "message": "Password changed successfully.",
    }    





from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.utils.security import decode_access_token
from src.utils.database import get_db
from src.users.models import UserModel,UserRole


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> UserModel:

    try:
        payload = decode_access_token(
            credentials.credentials
        )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = int(user_id)

    except HTTPException:
        raise

    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await db.scalar(
        select(UserModel).where(
            UserModel.id == user_id
        )
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive.",
        )

    return user




async def get_current_admin(current_user=Depends(get_current_user)):

    if current_user.role !=  UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="admin acces required"
        )

    return current_user


async def get_current_employer(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:

    if current_user.role != UserRole.employer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employer access required",
        )

    return current_user


async def get_current_job_seeker(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:

    if current_user.role != UserRole.job_seeker:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Job seeker access required",
        )

    return current_user


def require_role(*allowed_roles: UserRole):

    async def dependency(
        current_user: UserModel = Depends(get_current_user),
    ) -> UserModel:

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource.",
            )

        return current_user

    return dependency
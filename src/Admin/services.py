from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.users.models import (
    EmployerRequest,
    EmployerRequestStatus,
    UserModel,
    UserRole,
)

from .schemas import (
    EmployerRequestActionSchema,
    EmployerRequestCreateSchema,
)

from src.utils.email import( send_employer_approved_email,send_employer_rejected_email)

# ============================================================
# 1. User creates employer request
# ============================================================

async def create_employer_request(
    db: AsyncSession,
    request: EmployerRequestCreateSchema,
    current_user,
):
    # Check user is already employer
    if current_user.role == UserRole.employer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already an employer.",
        )

    # Check existing pending request
    result = await db.execute(
        select(EmployerRequest).where(
            EmployerRequest.user_id == current_user.id,
            EmployerRequest.status
            == EmployerRequestStatus.pending,
        )
    )

    existing_request = result.scalar_one_or_none()

    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a pending employer request.",
        )

    # Create request
    employer_request = EmployerRequest(
        user_id=current_user.id,
        reason=(
            request.reason.strip()
            if request.reason
            else None
        ),
        status=EmployerRequestStatus.pending,
    )

    db.add(employer_request)

    await db.commit()
    await db.refresh(employer_request)

    return employer_request


# ============================================================
# 2. User checks their latest employer request
# ============================================================

async def get_my_employer_request(
    db: AsyncSession,
    current_user,
):
    result = await db.execute(
        select(EmployerRequest)
        .where(
            EmployerRequest.user_id == current_user.id
        )
        .order_by(
            EmployerRequest.created_at.desc()
        )
    )

    employer_request = result.scalars().first()

    if not employer_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You have not submitted an employer request.",
        )

    return employer_request


# ============================================================
# 3. Admin gets all pending employer requests
# ============================================================

async def get_pending_employer_requests(
    db: AsyncSession,
):
    result = await db.execute(
        select(EmployerRequest)
        .options(
            selectinload(EmployerRequest.user)
        )
        .where(
            EmployerRequest.status
            == EmployerRequestStatus.pending
        )
        .order_by(
            EmployerRequest.created_at.desc()
        )
    )

    requests = result.scalars().all()

    return [
        {
            "id": request.id,
            "user_id": request.user_id,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
            "number": request.user.number,
            "address": request.user.address,
            "reason": request.reason,
            "status": request.status,
            "created_at": request.created_at,
        }
        for request in requests
    ]


# ============================================================
# 4. Admin gets one employer request details
# ============================================================

async def get_employer_request_details(
    db: AsyncSession,
    request_id: int,
):
    result = await db.execute(
        select(EmployerRequest)
        .options(
            selectinload(EmployerRequest.user)
        )
        .where(
            EmployerRequest.id == request_id
        )
    )

    employer_request = result.scalar_one_or_none()

    if not employer_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employer request not found.",
        )

    return {
        "id": employer_request.id,
        "user_id": employer_request.user_id,
        "first_name": employer_request.user.first_name,
        "last_name": employer_request.user.last_name,
        "email": employer_request.user.email,
        "number": employer_request.user.number,
        "address": employer_request.user.address,
        "reason": employer_request.reason,
        "status": employer_request.status,
        "created_at": employer_request.created_at,
    }


# ============================================================
# 5. Admin approves / rejects employer request
# ============================================================
async def action_employer_request(
    db: AsyncSession,
    request_id: int,
    action: EmployerRequestActionSchema,
):
    # Find employer request
    result = await db.execute(
        select(EmployerRequest).where(
            EmployerRequest.id == request_id
        )
    )

    employer_request = result.scalar_one_or_none()

    if not employer_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employer request not found.",
        )

    # Only pending request can be processed
    if (
        employer_request.status
        != EmployerRequestStatus.pending
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This employer request has already been processed.",
        )

    # Find user
    user_result = await db.execute(
        select(UserModel).where(
            UserModel.id == employer_request.user_id
        )
    )

    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    # ========================================================
    # Approve
    # ========================================================

    if action.status == "approve":

        employer_request.status = (
            EmployerRequestStatus.approved
        )

        user.role = UserRole.employer

        # Send approval email
        send_employer_approved_email(
            to_email=user.email,
            first_name=user.first_name,
        )

    # ========================================================
    # Reject
    # ========================================================

    elif action.status == "reject":

        employer_request.status = (
            EmployerRequestStatus.rejected
        )

        # Send rejection email
        send_employer_rejected_email(
            to_email=user.email,
            first_name=user.first_name,
        )

    # Save changes
    await db.commit()

    await db.refresh(employer_request)

    return employer_request
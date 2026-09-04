from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.depends.auth_depends import (
    get_current_user,
    get_current_admin,
)
from src.utils.database import get_db

from src.Admin.schemas import (
    EmployerRequestCreateSchema,
    EmployerRequestResponseSchema,
    EmployerRequestAdminResponseSchema,
    EmployerRequestActionSchema,
)

from src.Admin.services import (
    create_employer_request,
    get_my_employer_request,
    get_pending_employer_requests,
    get_employer_request_details,
    action_employer_request,
)




employers_router = APIRouter(
    prefix="/employer-requests",
    tags=["Employer Requests"],
)




@employers_router.post(
    "",
    response_model=EmployerRequestResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_employer_request_api(
    request: EmployerRequestCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await create_employer_request(
        db=db,
        request=request,
        current_user=current_user,
    )




@employers_router.get(
    "/me",
    response_model=EmployerRequestResponseSchema,
)
async def get_my_employer_request_api(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await get_my_employer_request(
        db=db,
        current_user=current_user,
    )



admin_employers_router = APIRouter(
    prefix="/admin/employer-requests",
    tags=["Admin Employer Requests"],
)




@admin_employers_router.get(
    "",
    response_model=list[EmployerRequestAdminResponseSchema],
)
async def get_pending_employer_requests_api(
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return await get_pending_employer_requests(
        db=db,
    )


# =============================
# 4. Admin gets one request details
# =================================

@admin_employers_router.get(
    "/{request_id}",
    response_model=EmployerRequestAdminResponseSchema,
)
async def get_employer_request_details_api(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return await get_employer_request_details(
        db=db,
        request_id=request_id,
    )


# ===================================
# 5. Admin approves / rejects request
# =====================================

@admin_employers_router.patch(
    "/{request_id}",
    response_model=EmployerRequestResponseSchema,
)
async def action_employer_request_api(
    request_id: int,
    action: EmployerRequestActionSchema,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    return await action_employer_request(
        db=db,
        request_id=request_id,
        action=action,
    )
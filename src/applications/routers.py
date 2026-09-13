
from fastapi import (
    APIRouter,
    Depends,
    status,
    UploadFile,
    File,
    Form,
)

from sqlalchemy.ext.asyncio import AsyncSession

from src.applications.schemas import (
    ResumeResponseSchema,
    ApplicationCreateSchema,
    ApplicationStatusUpdateSchema,
    EmployerApplicationResponseSchema,
)

from src.applications import services

from src.utils.database import get_db

from src.depends.auth_depends import (
    get_current_job_seeker,
    get_current_employer,
)

from src.users.models import UserModel


## ----------------
## Resume routes
## ----------------

resume_router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"],
)


@resume_router.post(
    "",
    response_model=ResumeResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_resume_route(
    title: str = Form(...),
    resume: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_job_seeker),
):
    return await services.create_resume(
        title=title,
        resume=resume,
        db=db,
        user_id=current_user.id,
    )


@resume_router.get(
    "",
    response_model=list[ResumeResponseSchema],
)
async def get_my_resumes_route(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_job_seeker),
):
    return await services.get_my_resumes(
        db=db,
        user_id=current_user.id,
    )


@resume_router.get(
    "/{resume_id}",
    response_model=ResumeResponseSchema,
)
async def get_my_resume_route(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_job_seeker),
):
    return await services.get_my_resume(
        db=db,
        resume_id=resume_id,
        user_id=current_user.id,
    )


@resume_router.delete(
    "/{resume_id}",
)
async def delete_resume_route(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_job_seeker),
):
    return await services.delete_resume_by_user(
        db=db,
        resume_id=resume_id,
        user_id=current_user.id,
    )


## ----------------
## Application routes
## ----------------

application_router = APIRouter(
    prefix="/applications",
    tags=["Applications"],
)


# ==================================================
# Job Seeker
# ==================================================


# Apply for a job
@application_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_application(
    request: ApplicationCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_job_seeker),
):
    return await services.create_application(
        db=db,
        request=request,
        job_seeker_id=current_user.id,
    )


# Get my applications
@application_router.get(
    "/my-applications",
    status_code=status.HTTP_200_OK,
)
async def get_my_applications(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_job_seeker),
):
    return await services.get_my_applications(
        db=db,
        job_seeker_id=current_user.id,
    )


# Get my application by ID
@application_router.get(
    "/my-applications/{application_id}",
    status_code=status.HTTP_200_OK,
)
async def get_my_application(
    application_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_job_seeker),
):
    return await services.get_application_by_id(
        db=db,
        application_id=application_id,
        job_seeker_id=current_user.id,
    )


# ==================================================
# Employer
# ==================================================


# Get ALL applications for employer's all jobs
@application_router.get(
    "/employer/all",
    status_code=status.HTTP_200_OK,
    response_model=list[EmployerApplicationResponseSchema],
)
async def get_all_employer_applications(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_employer),
):
    return await services.get_all_applications_for_employer(
        db=db,
        employer_id=current_user.id,
    )

## singale job seeker information get seen employerr 
@application_router.get(
    "/{application_id}",
    response_model=EmployerApplicationResponseSchema,
)
async def get_single_application_for_employer(
    application_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_employer),
):
    return await services.get_single_application_for_employer(
        db=db,
        application_id=application_id,
        employer_id=current_user["user_id"],
    )



# Accept / Reject application
@application_router.patch(
    "/{application_id}/status",
    status_code=status.HTTP_200_OK,
)
async def change_application_status(
    application_id: int,
    request: ApplicationStatusUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_employer),
):
    return await services.change_application_status(
        db=db,
        application_id=application_id,
        new_status=request.status,
        changed_by=current_user.id,
    )


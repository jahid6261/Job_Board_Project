from fastapi import HTTPException, status,UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.applications.models import (
    Resume,
    ApplicationModel,
    ApplicationStatus,
    ApplicationStatusHistory
)

from src.applications.schemas import (
    
    ApplicationCreateSchema,
)

from src.jobs.models import Job,Company
from src.utils.email import send_application_accepted_email,send_application_rejected_email
from src.utils.cloudinary import upload_resume,delete_resume
from src.users.models import UserModel
## ----------------
## Resume
## ----------------


async def create_resume(
    title: str,
    resume: UploadFile,
    db: AsyncSession,
    user_id: int,
):

    result = await upload_resume(resume)

    new_resume = Resume(
        job_seeker_id=user_id,
        title=title,
        resume_url=result["resume_url"],
        public_id=result["public_id"],
    )

    db.add(new_resume)

    await db.commit()
    await db.refresh(new_resume)

    return new_resume


async def get_my_resumes(
    db: AsyncSession,
    user_id: int,
):

    result = await db.execute(
        select(Resume).where(
            Resume.job_seeker_id == user_id,
            Resume.is_active == True,
        )
    )

    return result.scalars().all()


async def get_my_resume(
    db: AsyncSession,
    resume_id: int,
    user_id: int,
):

    result = await db.execute(
        select(Resume).where(
            Resume.id == resume_id,
            Resume.job_seeker_id == user_id,
            Resume.is_active == True,
        )
    )

    resume = result.scalar_one_or_none()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    return resume


async def delete_resume_by_user(
    db: AsyncSession,
    resume_id: int,
    user_id: int,
):

    result = await db.execute(
        select(Resume).where(
            Resume.id == resume_id,
            Resume.job_seeker_id == user_id,
            Resume.is_active == True,
        )
    )

    resume = result.scalar_one_or_none()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    try:
        await delete_resume(resume.public_id)

        await db.delete(resume)

        await db.commit()

    except Exception as e:

        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete resume",
        )

    return {
        "success": True,
        "message": "Resume deleted successfully",
    }

## ----------------
## Application for job seeker 
## ----------------


async def create_application(
    db: AsyncSession,
    request: ApplicationCreateSchema,
    job_seeker_id: int,
):

    resume_result=await db.execute(
        select(Resume).where(
            Resume.id==request.resume_id,
            Resume.job_seeker_id==job_seeker_id,
            Resume.is_active==True,
        )
    )

    resume=resume_result.scalar_one_or_none()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )


    job_result=await db.execute(
        select(Job).where(
            Job.id==request.job_id,
            Job.is_active==True,
        )
    )

    job=job_result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )


    existing_result=await db.execute(
        select(ApplicationModel).where(
            ApplicationModel.job_id==request.job_id,
            ApplicationModel.job_seeker_id==job_seeker_id,
        )
    )

    existing_application=existing_result.scalar_one_or_none()

    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied for this job",
        )


    application=ApplicationModel(
        job_id=request.job_id,
        job_seeker_id=job_seeker_id,
        resume_id=request.resume_id,
        cover_letter=request.cover_letter,
        status=ApplicationStatus.PENDING,
    )

    db.add(application)

    await db.commit()

    await db.refresh(application)

    return application


async def get_my_applications(
    db: AsyncSession,
    job_seeker_id: int,
):
    result = await db.execute(
        select(ApplicationModel)
        .where(ApplicationModel.job_seeker_id == job_seeker_id)
        .order_by(ApplicationModel.applied_at.desc())
    )

    applications = result.scalars().all()

    return applications




async def get_application_by_id(
    db: AsyncSession,
    application_id: int,
    job_seeker_id: int,
):
    result = await db.execute(
        select(ApplicationModel)
        .where(
            ApplicationModel.id == application_id,
            ApplicationModel.job_seeker_id == job_seeker_id,
        )
    )

    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    return application

####

#job seeker application seen owner employer 
#####

async def get_all_applications_for_employer(
    db: AsyncSession,
    employer_id: int,
):
    result = await db.execute(
        select(
            ApplicationModel,
            Job,
            UserModel,
            Resume,
        )
        .join(Job, ApplicationModel.job_id == Job.id)
        .join(UserModel, ApplicationModel.job_seeker_id == UserModel.id)
        .join(Resume, ApplicationModel.resume_id == Resume.id)
        .where(
            Job.employer_id == employer_id
        )
        .order_by(
            ApplicationModel.applied_at.desc()
        )
    )

    rows = result.all()

    return [
        {
            "id": application.id,

            "job": {
                "id": job.id,
                "title": job.title,
            },

            "candidate": {
                "name": f"{user.first_name} {user.last_name}".strip(),
                "email": user.email,
                "phone": user.number,
            },

            "resume": {
                "title": resume.title,
                "resume_url": resume.resume_url,
            },

            "cover_letter": application.cover_letter,
            "status": application.status,
            "applied_at": application.applied_at,
            "updated_at": application.updated_at,
        }
        for application, job, user, resume in rows
    ]

async def get_single_application_for_employer(
    db: AsyncSession,
    application_id: int,
    employer_id: int,
):
    result = await db.execute(
        select(
            ApplicationModel,
            Job,
            UserModel,
            Resume,
        )
        .join(Job, ApplicationModel.job_id == Job.id)
        .join(
            UserModel,
            ApplicationModel.job_seeker_id == UserModel.id,
        )
        .join(
            Resume,
            ApplicationModel.resume_id == Resume.id,
        )
        .where(
            ApplicationModel.id == application_id,
            Job.employer_id == employer_id,
        )
    )

    row = result.one_or_none()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    application, job, user, resume = row

    return {
        "id": application.id,

        "job": {
            "id": job.id,
            "title": job.title,
        },

        "candidate": {
            "name": f"{user.first_name} {user.last_name}".strip(),
            "email": user.email,
            "phone": user.number,
        },

        "resume": {
            "title": resume.title,
            "resume_url": resume.resume_url,
        },

        "cover_letter": application.cover_letter,
        "status": application.status,
        "applied_at": application.applied_at,
        "updated_at": application.updated_at,
    }

async def change_application_status(
    db: AsyncSession,
    application_id: int,
    new_status: ApplicationStatus,
    changed_by: int,
):
    result = await db.execute(
        select(ApplicationModel, Job, Company, UserModel)
        .join(Job, ApplicationModel.job_id == Job.id)
        .join(Company, Job.company_id == Company.id)
        .join(UserModel, ApplicationModel.job_seeker_id == UserModel.id)
        .where(
            ApplicationModel.id == application_id
        )
    )

    row = result.one_or_none()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    application, job, company, job_seeker = row

    if job.employer_id != changed_by:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to change this application status",
        )

    old_status = application.status

    if old_status == new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Application is already {new_status.value}",
        )

    application.status = new_status

    history = ApplicationStatusHistory(
        application_id=application.id,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by,
    )

    db.add(history)

    try:
        await db.commit()
        await db.refresh(application)

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update application status",
        )

    # Send email only for ACCEPTED / REJECTED
    if new_status == ApplicationStatus.ACCEPTED:

        result = send_application_accepted_email(
        to_email=job_seeker.email,
        first_name=job_seeker.first_name,
        application_id=application.id,
        job_title=job.title,
        company_name=company.name,
    )

        print("ACCEPTED EMAIL RESULT:", result)

    elif new_status == ApplicationStatus.REJECTED:

        result = send_application_rejected_email(
        to_email=job_seeker.email,
        first_name=job_seeker.first_name,
        application_id=application.id,
        job_title=job.title,
        company_name=company.name,
    )

    print("REJECTED EMAIL RESULT:", result)
    return application
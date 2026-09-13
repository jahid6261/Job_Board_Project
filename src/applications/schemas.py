

from datetime import datetime
from pydantic import BaseModel, ConfigDict
from src.applications.models import ApplicationStatus

class ResumeResponseSchema(BaseModel): 
    id: int
    job_seeker_id: int
    title: str
    resume_url: str 
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ApplicationCreateSchema(BaseModel):

    job_id: int
    resume_id: int
    cover_letter: str | None = None


class ApplicationResponseSchema(BaseModel):

    id: int
    job_id: int
    job_seeker_id: int
    resume_id: int
    cover_letter: str | None
    status: str
    applied_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationStatusUpdateSchema(BaseModel):
    status: ApplicationStatus


class ApplicationStatusHistoryResponseSchema(BaseModel):
    id: int
    application_id: int
    old_status: ApplicationStatus | None
    new_status: ApplicationStatus
    changed_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class EmployerJobResponseSchema(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)


class EmployerCandidateResponseSchema(BaseModel):
    name: str
    email: str
    phone: str


class EmployerResumeResponseSchema(BaseModel):
    title: str
    resume_url: str

    model_config = ConfigDict(from_attributes=True)


class EmployerApplicationResponseSchema(BaseModel):
    id: int

    job: EmployerJobResponseSchema
    candidate: EmployerCandidateResponseSchema
    resume: EmployerResumeResponseSchema

    cover_letter: str | None
    status: ApplicationStatus
    applied_at: datetime
    updated_at: datetime
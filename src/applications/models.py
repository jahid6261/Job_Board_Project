import enum
from sqlalchemy import Column,Integer,String,Boolean,DateTime,ForeignKey,Text,UniqueConstraint,Enum
from sqlalchemy.sql import func
from src.utils.database import DBModel
from sqlalchemy.orm import relationship

class Resume(DBModel):

    __tablename__ = "resumes"

    id=Column(Integer,primary_key=True,index=True)
    job_seeker_id=Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False,index=True)


    title=Column(String(100),nullable=False)
    resume_url=Column(String(500),nullable=False)
    public_id = Column(String(255), nullable=False)
    is_active=Column(Boolean,default=True,nullable=False)

    created_at=Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at=Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)


    job_seeker = relationship("UserModel", back_populates="resumes")
    applications = relationship("ApplicationModel", back_populates="resume") 


 



class ApplicationStatus(enum.Enum):

    PENDING="PENDING"
    REVIEWED="REVIEWED"
    ACCEPTED="ACCEPTED"
    REJECTED="REJECTED"


class ApplicationModel(DBModel):

    __tablename__ = "applications"

    __table_args__=(UniqueConstraint("job_id","job_seeker_id",name="uq_application_job_job_seeker"),)

    id=Column(Integer,primary_key=True,index=True)
    job_id=Column(Integer,ForeignKey("jobs.id",ondelete="CASCADE"),nullable=False,index=True)
    job_seeker_id=Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False,index=True)
    resume_id=Column(Integer,ForeignKey("resumes.id",ondelete="RESTRICT"),nullable=False,index=True)

    cover_letter=Column(Text,nullable=True)
    status=Column(Enum(ApplicationStatus),default=ApplicationStatus.PENDING,nullable=False,index=True)


    applied_at=Column(DateTime(timezone=True),server_default=func.now(),
                      nullable=False)
    updated_at=Column(DateTime(timezone=True),server_default=func.now(),
                      onupdate=func.now(),nullable=False)

    resume = relationship("Resume", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    job_seeker = relationship("UserModel", back_populates="applications")
    status_history = relationship(
    "ApplicationStatusHistory",
    back_populates="application",
    cascade="all, delete-orphan",
)


class ApplicationStatusHistory(DBModel):

    __tablename__= "application_status_history"

    id=Column(Integer,primary_key=True,index=True)
    application_id=Column(Integer,ForeignKey("applications.id",ondelete="CASCADE"),
                          nullable=False,index=True)
    old_status=Column(Enum(ApplicationStatus),
                      nullable=True)
    new_status=Column(Enum(ApplicationStatus),nullable=False)
    changed_by=Column(Integer,ForeignKey("users.id",ondelete="RESTRICT"),nullable=False,index=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


    application = relationship(
    "ApplicationModel",
    back_populates="status_history",
)

    changed_by_user = relationship(
    "UserModel",
    back_populates="status_changes",
)
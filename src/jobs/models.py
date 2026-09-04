
from sqlalchemy import  Column,Integer,String,Boolean,DateTime,ForeignKey,func,Text
from sqlalchemy.orm import relationship

from sqlalchemy import UniqueConstraint


from src.utils.database import DBModel


class Category(DBModel):

    __tablename__ = "categories"

    id=Column(Integer,primary_key=True,index=True)
    title=Column(String(100), unique=True, nullable=False)
    slug=Column(String(100), unique=True,nullable=False)
    description=Column(Text,nullable=False)

    created_at = Column(  
            DateTime(timezone=True),
            server_default=func.now(),
        )
    
    updated_at = Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        )
    
    jobs = relationship("Job", back_populates="category") 


class Company(DBModel):

    __tablename__ = "companies"
    id=Column(Integer,primary_key=True,index=True)
    employer_id = Column(
    Integer,
    ForeignKey("users.id", ondelete="CASCADE"),
    nullable=False,
    unique=True,
    index=True
)
    name=Column(String(100),nullable=False,unique=True)
    description=Column(Text,nullable=False)
    logo_url=Column(String(255),nullable=True)
    website =Column(String(255),nullable=True)
    location=Column(String(255),nullable=True)
    industry=Column(String(100),nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    employer = relationship("UserModel", back_populates="companies")
    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")


class Job(DBModel):
    __tablename__ = "jobs"

    __table_args__ = (
    UniqueConstraint(
        "company_id",
        "slug",
        name="uq_job_company_slug",
    ),
)
    
    id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    slug=Column(String(100),nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=False)
    location = Column(String(150), nullable=False)
    salary_min = Column(Integer, nullable=True)  
    salary_max = Column(Integer, nullable=True)  
    application_deadline = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    employer = relationship("UserModel", back_populates="jobs")
    company = relationship("Company", back_populates="jobs")
    category = relationship("Category", back_populates="jobs")
   
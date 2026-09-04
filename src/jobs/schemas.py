from pydantic import BaseModel, Field, ConfigDict, HttpUrl
from datetime import datetime
from typing import Optional


##------------
##  Category 
##------------


class CategoryCreate(BaseModel):
    title: str = Field(..., max_length=150)
    slug: str = Field(..., max_length=150)
    description: str


class CategoryUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=150)
    slug: Optional[str] = Field(None, max_length=150)
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    title: str
    slug: str
    description: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
class BulkCategoryResponse(BaseModel):
    message: str
    count: int    


class CategoryBulkDelete(BaseModel):
    ids: list[int]


## Company Schemas 



class CompanyCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=10)
    logo_url: HttpUrl | None = None
    website: HttpUrl | None = None
    location: str | None = Field(None, max_length=255)
    industry: str | None = Field(None, max_length=100)    

class CompanyResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employer_id: int
    name: str
    description: str
    logo_url: str | None
    website: str | None
    location: str | None
    industry: str | None    

class CompanyUpdateSchema(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    description: str | None = Field(None, min_length=10)
    logo_url: HttpUrl | None = None
    website: HttpUrl | None = None
    location: str | None = Field(None, max_length=255)
    industry: str | None = Field(None, max_length=100)




#--------------
## JOBS SCHEMA
#------------

class JobCreateSchema(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    requirements: str = Field(..., min_length=10)
    category_id: int | None = None
    location: str = Field(..., min_length=2, max_length=150)
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    application_deadline: datetime

class JobUpdateSchema(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, min_length=10)
    requirements: str | None = Field(default=None, min_length=10)
    category_id: int | None = None
    location: str | None = Field(default=None, min_length=2, max_length=150)
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    application_deadline: datetime | None = None
    is_active: bool | None = None

class JobCategoryResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str

class JobCompanyResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    logo_url: str | None
    website: str | None
    location: str | None
    industry: str | None

class JobResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    slug: str
    description: str
    requirements: str
    location: str
    salary_min: int | None
    salary_max: int | None
    application_deadline: datetime
    is_active: bool
    category: JobCategoryResponseSchema | None
    company: JobCompanyResponseSchema
    created_at: datetime
    updated_at: datetime | None
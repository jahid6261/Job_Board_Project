from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.jobs.schemas import (BulkCategoryResponse, CategoryCreate, CategoryUpdate, CategoryResponse, CategoryBulkDelete,
                              CompanyCreateSchema,CompanyResponseSchema,CompanyUpdateSchema,
                              JobCreateSchema,JobResponseSchema,JobUpdateSchema,
)

from src.jobs import services
from src.utils.database import get_db
from src.depends.auth_depends import get_current_admin  ,get_current_user
from src.users.models import UserModel


## ------
## Categorirs routes 

categories_router = APIRouter(prefix="/categories", tags=["Categories"])


@categories_router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    request: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin), 
):
    return await services.create_category(request, db)


@categories_router.post("/bulk", response_model=BulkCategoryResponse)
async def create_bulk_categories(
    request: List[CategoryCreate],
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin),  
):
    return await services.create_bulk_categories(request, db)


@categories_router.get("/", response_model=list[CategoryResponse])
async def get_categories(
    db: AsyncSession = Depends(get_db),
):
    return await services.get_all_categories(db)

@categories_router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await services.get_category_by_id(category_id, db)


@categories_router.put("/{category_id}")
async def update_category(
    category_id: int,
    request: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await services.update_category(
        category_id,
        request,
        db,
    )


@categories_router.patch("/{category_id}")
async def patch_category(
    category_id: int,
    request: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await services.patch_category(
        category_id,
        request,
        db,
    )

@categories_router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await services.delete_category(
        category_id,
        db,
    )

@categories_router.delete("/bulk")
async def bulk_delete_category(
    request: CategoryBulkDelete,
    db: AsyncSession = Depends(get_db),
):
    return await services.bulk_delete_category(
        request,
        db,
    )


## -------
## Company routes
## ------------

company_router = APIRouter(
    prefix="/companies",
    tags=["Company"],
)


@company_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_company_route(
    request: CompanyCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.create_company(
        db=db,
        request=request,
        employer_id=current_user.id,
    )


@company_router.get(
    "",
    response_model=list[CompanyResponseSchema],
)
async def get_companies_route(
    db: AsyncSession = Depends(get_db),
):
    return await services. get_companies(db)


@company_router.get(
    "/{company_id}",
    response_model=CompanyResponseSchema,
)
async def get_company_route(
    company_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await services.get_company(
        db=db,
        company_id=company_id,
    )


@company_router.patch("/{company_id}")
async def patch_company_route(
    company_id: int,
    request: CompanyUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.patch_company(
        company_id=company_id,
        request=request,
        db=db,
        employer_id=current_user.id,
    )


@company_router.delete("/{company_id}")
async def delete_company_route(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.delete_company(
        company_id=company_id,
        db=db,
        current_user=current_user,
    )



## ----------
## jobs routes
##----------

jobs_router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


@jobs_router.post(
    "",
    response_model=JobResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_job_api(
    request: JobCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.create_job(
        db=db,
        request=request,
        current_user=current_user,
    )


@jobs_router.get("/jobs")
async def get_jobs(
    search: str | None = None,
    category_id: int | None = None,
    location: str | None = None,
    page: int = 1,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    return await services. get_all_jobs(
        db=db,
        search=search,
        category_id=category_id,
        location=location,
        page=page,
        limit=limit,
    )


@jobs_router.get("/{job_id}", response_model=JobResponseSchema)
async def get_job_details_api(
    job_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await services.get_job_details(db, job_id)



@jobs_router.patch(
    "/{job_id}",
    
)
async def update_job_api(
    job_id: int,
    request: JobUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.update_job(
        db=db,
        job_id=job_id,
        request=request,
        current_user=current_user,
    )
@jobs_router.delete("/{job_id}")
async def delete_job_api(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await services.delete_job(
        db=db,
        job_id=job_id,
        current_user=current_user,
    )
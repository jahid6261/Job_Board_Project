from  sqlalchemy import select,update,delete,or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload


from src.jobs.models import (Category,Company,Job)
from src.jobs.schemas import (CategoryCreate,CategoryUpdate,CategoryBulkDelete,CompanyCreateSchema,CompanyUpdateSchema,
                              JobCreateSchema,JobUpdateSchema

                              )
from src.users.models import UserRole


## ---------

## CATEGORY CRUD
##----------

async def create_category(request: CategoryCreate, db: AsyncSession):
    existing = await db.scalar(
        select(Category).where(
            (Category.title == request.title) | (Category.slug == request.slug)
        )
    )
    if existing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Category already exists")

    category = Category(
        title=request.title.strip(),
        slug=request.slug.strip(),
        description=request.description.strip()
    )

    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def create_bulk_categories(request: list[CategoryCreate], db: AsyncSession):
    categories = [Category(**item.model_dump()) for item in request]

    db.add_all(categories)
    await db.commit()
    return {"message": "Categories created", "count": len(categories)}

async def get_all_categories(db: AsyncSession):
    result = await db.execute(
        select(Category)
    )

    return result.scalars().all()


async def get_category_by_id(
    category_id: int,
    db: AsyncSession,
):
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )

    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    return category



async def update_category(
    category_id: int,
    request: CategoryUpdate,
    db: AsyncSession,
):
    result = await db.execute(
        update(Category)
        .where(Category.id == category_id)
        .values(
            title=request.title.strip(),
            slug=request.slug.strip(),
            description=request.description.strip(),
        )
    )

    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    await db.commit()

    return {"message": "Category updated successfully"}


async def patch_category(
    category_id: int,
    request: CategoryUpdate,
    db: AsyncSession,
):
    update_data = request.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No data provided",
        )

    if "title" in update_data:
        update_data["title"] = update_data["title"].strip()

    if "slug" in update_data:
        update_data["slug"] = update_data["slug"].strip()

    if "description" in update_data:
        update_data["description"] = update_data["description"].strip()

    result = await db.execute(
        update(Category)
        .where(Category.id == category_id)
        .values(**update_data)
    )

    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    await db.commit()

    return {"message": "Category updated successfully"}


async def delete_category(
    category_id: int,
    db: AsyncSession,
):
    result = await db.execute(
        delete(Category)
        .where(Category.id == category_id)
    )

    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    await db.commit()

    return {
        "message": "Category deleted successfully"
    }



async def bulk_delete_category(
    request: CategoryBulkDelete,
    db: AsyncSession,
):
    if not request.ids:
        raise HTTPException(
            status_code=400,
            detail="No ids provided",
        )

    result = await db.execute(
        delete(Category)
        .where(Category.id.in_(request.ids))
    )

    await db.commit()

    return {
        "message": f"{result.rowcount} categories deleted successfully"
    }

##----------------------
## COMPNAY CRUD
## ----------------------

async def create_company(
    db: AsyncSession,
    request: CompanyCreateSchema,
    employer_id: int,
):
    # Check employer already has a company
    result = await db.execute(
        select(Company).where(
            Company.employer_id == employer_id
        )
    )

    existing_company = result.scalar_one_or_none()

    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a company.",
        )

    company = Company(
        employer_id=employer_id,
        name=request.name.strip(),
        description=request.description.strip(),
        logo_url=str(request.logo_url).strip() if request.logo_url else None,
        website=str(request.website).strip() if request.website else None,
        location=request.location.strip() if request.location else None,
        industry=request.industry.strip().lower() if request.industry else None,
    )

    db.add(company)

    await db.commit()
    await db.refresh(company)

    return company

async def get_companies(
    db: AsyncSession,
):
    result = await db.execute(
        select(Company)
        .order_by(Company.created_at.desc())
    )

    companies = result.scalars().all()

    return companies


async def get_company(
    db: AsyncSession,
    company_id: int,
):
    result = await db.execute(
        select(Company).where(
            Company.id == company_id
        )
    )

    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        )

    return company


async def patch_company(
    company_id: int,
    request: CompanyUpdateSchema,
    db: AsyncSession,
    employer_id: int,
):
    update_data = request.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided"
        )

    if "name" in update_data:
        update_data["name"] = update_data["name"].strip()

    if "description" in update_data:
        update_data["description"] = update_data["description"].strip()

    if "logo_url" in update_data:
        update_data["logo_url"] = (
            str(update_data["logo_url"]).strip()
            if update_data["logo_url"]
            else None
        )

    if "website" in update_data:
        update_data["website"] = (
            str(update_data["website"]).strip()
            if update_data["website"]
            else None
        )

    if "location" in update_data:
        update_data["location"] = (
            update_data["location"].strip()
            if update_data["location"]
            else None
        )

    if "industry" in update_data:
        update_data["industry"] = (
            update_data["industry"].strip().lower()
            if update_data["industry"]
            else None
        )

    result = await db.execute(
        update(Company)
        .where(
            Company.id == company_id,
            Company.employer_id == employer_id
        )
        .values(**update_data)
    )

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found or you don't have permission"
        )

    await db.commit()

    return {"message": "Company updated successfully"}

async def delete_company(
    company_id: int,
    db: AsyncSession,
    current_user,
):
    if current_user.role == "admin":
        result = await db.execute(
            delete(Company).where(
                Company.id == company_id
            )
        )

    else:
        result = await db.execute(
            delete(Company).where(
                Company.id == company_id,
                Company.employer_id == current_user.id
            )
        )

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found or you don't have permission"
        )

    await db.commit()

    return {"message": "Company deleted successfully"}


##-----------------------
## CRUD JOB
##-------
async def create_job(
    db: AsyncSession,
    request: JobCreateSchema,
    current_user,
):
    if current_user.role != UserRole.employer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can create jobs."
        )

    result = await db.execute(
        select(Company).where(
            Company.employer_id == current_user.id
        )
    )
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found."
        )

    if request.category_id is not None:
        result = await db.execute(
            select(Category).where(
                Category.id == request.category_id
            )
        )
        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found."
            )

    job = Job(
        employer_id=current_user.id,
        company_id=company.id,
        category_id=request.category_id,
        title=request.title,
        slug=request.title.lower().replace(" ", "-"),
        description=request.description,
        requirements=request.requirements,
        location=request.location,
        salary_min=request.salary_min,
        salary_max=request.salary_max,
        application_deadline=request.application_deadline,
        is_active=True,
    )

    db.add(job)
    await db.commit()

    result = await db.execute(
    select(Job)
    .options(
        selectinload(Job.category),
        selectinload(Job.company),
    )
    .where(Job.id == job.id)
)

    job = result.scalar_one()

    return job



async def get_all_jobs(
    db: AsyncSession,
    search: str | None = None,
    category_id: int | None = None,
    location: str | None = None,
    page: int = 1,
    limit: int = 10,
):
    query = (
        select(Job)
        .options(
            selectinload(Job.company),
            selectinload(Job.category),
        )
    )

    # Search
    if search:
        query = query.where(
            or_(
                Job.title.ilike(f"%{search}%"),
                Job.description.ilike(f"%{search}%"),
            )
        )

    # Category filter
    if category_id:
        query = query.where(
            Job.category_id == category_id
        )

    # Location filter
    if location:
        query = query.where(
            Job.location.ilike(f"%{location}%")
        )

    # Pagination
    offset = (page - 1) * limit

    query = (
        query
        .order_by(Job.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(query)

    return result.scalars().all()

async def get_job_details(db: AsyncSession, job_id: int):
    result = await db.execute(
        select(Job)
        .options(
            selectinload(Job.company),
            selectinload(Job.category),
        )
        .where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found."
        )

    return job


async def update_job(
    db: AsyncSession,
    job_id: int,
    request: JobUpdateSchema,
    current_user,
):
    result = await db.execute(
        select(Job).where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found."
        )

    if current_user.role != UserRole.employer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can update jobs."
        )

    if job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own jobs."
        )

    if request.category_id is not None:
        result = await db.execute(
            select(Category).where(Category.id == request.category_id)
        )
        category = result.scalar_one_or_none()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found."
            )

    update_data = request.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(job, field, value)

    await db.commit()

    return {"message": "Job updated successfully."}

async def delete_job(
    db: AsyncSession,
    job_id: int,
    current_user,
):
    result = await db.execute(
        select(Job).where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found."
        )

    if current_user.role != UserRole.employer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can delete jobs."
        )

    if job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own jobs."
        )

    await db.delete(job)
    await db.commit()

    return {"message": "Job deleted successfully."}
from fastapi import FastAPI,APIRouter
import uvicorn

from src.users.routers import users_router
from src.jobs.routers import categories_router,company_router,jobs_router
from src.Admin.routers import employers_router,admin_employers_router
from src.applications.routers import resume_router,application_router

app=FastAPI()

api_v1=APIRouter(prefix='/api/v1')

api_v1.include_router(users_router)
api_v1.include_router(categories_router)
api_v1.include_router(company_router)
api_v1.include_router(jobs_router)
api_v1.include_router(resume_router)
api_v1.include_router(application_router)
api_v1.include_router(employers_router)
api_v1.include_router(admin_employers_router)


app.include_router(api_v1)


@app.get("/")

def read_root():

    return{
        "message": "welcome to  my job board proeject"
    }


if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

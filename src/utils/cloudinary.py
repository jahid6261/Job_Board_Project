import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from src.utils.settings import settings


cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)





async def upload_resume(resume: UploadFile):

    result = cloudinary.uploader.upload(
        resume.file,
        folder="resumes",
        resource_type="raw",
        public_id=resume.filename
    )

    return {
        "resume_url": result["secure_url"],
        "public_id": result["public_id"],
    }





async def delete_resume(public_id: str):

    result = cloudinary.uploader.destroy(
        public_id,
        resource_type="raw"
    )

    if result.get("result") != "ok":
        raise Exception("Resume deletion failed")

    return result
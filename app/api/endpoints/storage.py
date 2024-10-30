from fastapi import APIRouter, File, UploadFile

from app.services.storage import save_avatar_image

router = APIRouter()


@router.post("/api/storage/upload", status_code=200)
async def upload_image(avatar: UploadFile = File):
    """Endpoint для загрузки аватара"""
    return await save_avatar_image(avatar)

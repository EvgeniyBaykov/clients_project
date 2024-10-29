import aiofiles
import io
import os
import uuid
from fastapi import UploadFile
from PIL import Image
from app.core.config import settings

UPLOAD_DIRECTORY = "uploads/avatars"


async def add_watermark(avatar_path: str, watermark_path: str, output_path: str) -> str:
    """Накладывает водяной знак на аватар и сохраняет его."""

    avatar = Image.open(avatar_path).convert("RGBA")
    watermark = Image.open(watermark_path).convert("RGBA")

    watermark = watermark.resize((avatar.width // 5, avatar.height // 5), Image.Resampling.LANCZOS)
    watermark_position = (avatar.width - watermark.width - 10, avatar.height - watermark.height - 10)

    combined = Image.new("RGBA", avatar.size)
    combined.paste(avatar, (0, 0))
    combined.paste(watermark, watermark_position, watermark)

    final_image = combined.convert("RGB")

    async with aiofiles.open(output_path, "wb") as f:
        img_byte_arr = io.BytesIO()
        final_image.save(img_byte_arr, format='JPEG')
        await f.write(img_byte_arr.getvalue())

    return output_path


async def save_avatar_image(avatar: UploadFile) -> str:
    """
    Функция получает картинку, извлекает расширение, генерирует уникальное название, чтобы избежать коллизий,
    создаёт папку для аватаров, если она не существует, асинхронно записывает файл на диск,
    накладывает водяной знак и возвращает путь до файла.
    """
    avatar_extension: str = avatar.filename.split(".")[-1]
    avatar_name: str = f"{uuid.uuid4()}.{avatar_extension}"
    avatar_name_with_watermark: str = f"water_{avatar_name}"
    avatar_path: str = os.path.join(UPLOAD_DIRECTORY, avatar_name)
    avatar_path_with_watermark: str = os.path.join(UPLOAD_DIRECTORY, avatar_name_with_watermark)

    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

    async with aiofiles.open(avatar_path, "wb") as out_file:
        while content := await avatar.read(1024):
            await out_file.write(content)

    watermark_path = settings.PATH_TO_AVATAR_WATERMARK

    file_with_watermark_path = await add_watermark(avatar_path, watermark_path, avatar_path_with_watermark)
    return file_with_watermark_path

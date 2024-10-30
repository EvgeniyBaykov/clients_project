from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.db.session import get_session
from app.models import Client
from app.repositories.client import ClientRepository
from app.core.config import settings
from app.services.client import get_current_user


async def rate_limit_middleware(session: AsyncSession = Depends(get_session),
                                current_user: Client = Depends(get_current_user)):
    """
    Middleware проверяет авторизован ли пользователь, вызывает функцию для проверки количества оценок
    за определенный промежуток времени, если оценок больше заданного количества, выбрасывает ошибку
    """

    if not current_user:
        raise HTTPException(status_code=401, detail="Необходима авторизация")

    twenty_four_hours_ago = datetime.now() - timedelta(days=1)
    client_repo = ClientRepository(session)
    ratings = await client_repo.get_ratings_by_client(current_user, twenty_four_hours_ago)

    if len(ratings) >= settings.RATINGS_PER_DAY:
        raise HTTPException(
            status_code=429,
            detail="Достигнут лимит оценок в день. Попробуйте позже."
        )

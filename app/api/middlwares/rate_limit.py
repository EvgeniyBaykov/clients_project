from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_session
from app.models import Client
from app.repositories.client import ClientRepository
from app.services.client import get_current_user


async def rate_limit(
    current_user: Client = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    """
    Вызывает функцию для проверки количества оценок за определенный промежуток времени,
    если оценок больше заданного количества, выбрасывает ошибку
    """

    twenty_four_hours_ago = datetime.now() - timedelta(days=1)
    client_repo = ClientRepository(session)
    ratings = await client_repo.get_ratings_by_client(
        current_user, twenty_four_hours_ago
    )

    if len(ratings) >= settings.RATINGS_PER_DAY:
        raise HTTPException(
            status_code=429, detail="Достигнут лимит оценок в день. Попробуйте позже."
        )

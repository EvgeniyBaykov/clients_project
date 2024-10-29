from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.client import ClientRepository
from app.schemas.client import ClientCreate


async def create_client_f(client_data: ClientCreate,
                          session: AsyncSession):
    """
    Создаем экземпляр репозитория для работы с клиентами, проверяет существование email,
    сохраняет аватар, если загружен, создаёт нового пользователя через репозиторий.
    """
    client_repo = ClientRepository(session)
    if await client_repo.get_by_email(client_data.email):
        raise HTTPException(status_code=400, detail="Данный email уже используется")

    new_client = await client_repo.create_client(client_data)
    return new_client

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.client import Client
from app.schemas.client import ClientCreate


class ClientRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> Client | None:
        """Проверка существования клиента с указанным email."""
        result = await self.session.execute(select(Client).where(Client.email == email))
        return result.scalars().first()

    async def create_client(self, client_data: ClientCreate) -> Client:
        """Создание нового клиента и сохранение в базе данных."""
        new_client = Client(
            first_name=client_data.first_name,
            last_name=client_data.last_name,
            email=client_data.email,
            gender=client_data.gender,
            avatar=client_data.avatar_url
        )
        self.session.add(new_client)
        await self.session.commit()
        await self.session.refresh(new_client)
        return new_client
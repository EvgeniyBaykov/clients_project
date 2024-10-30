from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.client import Client
from app.models.match import Match
from app.schemas.client import ClientCreate


class ClientRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> Client | None:
        """Возвращает клиента с указанным email."""
        result = await self.session.execute(select(Client).where(Client.email == email))
        return result.scalars().first()

    async def get_by_id(self, client_id: int) -> Client | None:
        """Возвращает клиента с указанным email."""
        result = await self.session.execute(select(Client).where(Client.id == client_id))
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
        new_client.set_password(client_data.password)
        self.session.add(new_client)
        await self.session.commit()
        await self.session.refresh(new_client)
        return new_client

    async def check_mutual_match(self, client_id, target_client_id):
        """
        Проверяет, существует ли взаимная симпатия между текущим пользователем и target_client_id.
        """
        query = (select(Match).where(Match.client_id == target_client_id, Match.target_id == client_id))
        result = await self.session.execute(query)
        match = result.scalars().first()
        return match is not None

    async def add_match(self, current_user_id, target_client_id):
        """
        Добавляет симпатию от текущего пользователя к target_client_id.
        """
        new_match = Match(client_id=current_user_id, target_id=target_client_id)
        self.session.add(new_match)
        await self.session.commit()

    async def get_ratings_by_client(self, current_user, since_time):
        """
        Возвращает список оценок пользователя других пользователей
        за определенный промежуток времени
        """
        stmt = select(Match).filter(Match.client_id == current_user.id, Match.created_at >= since_time)
        result = await self.session.execute(stmt)
        ratings = result.scalars().all()
        return ratings

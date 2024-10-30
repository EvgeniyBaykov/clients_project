from datetime import datetime
from typing import Sequence

from fastapi import HTTPException, Request
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.client import Client
from app.models.match import Match
from app.schemas.client import ClientCreate
from app.utils import calculate_distance, get_location


class ClientRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> Client | None:
        """Возвращает клиента с указанным email."""
        result = await self.session.execute(select(Client).where(Client.email == email))
        return result.scalars().first()

    async def get_by_id(self, client_id: int) -> Client | None:
        """Возвращает клиента с указанным email."""
        result = await self.session.execute(
            select(Client).where(Client.id == client_id)
        )
        return result.scalars().first()

    async def get_clients(
        self,
        current_user: Client,
        gender: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        distance: float | None = None,
        created_at: datetime | None = None
    ) -> Sequence[Client]:
        query = select(Client)

        conditions = []

        if gender:
            conditions.append(Client.gender == gender)
        if first_name:
            conditions.append(Client.first_name.ilike(f"%{first_name}%"))
        if last_name:
            conditions.append(Client.last_name.ilike(f"%{last_name}%"))
        if created_at:
            conditions.append((Client.created_at.ilike(f"%{created_at}%")))

        if conditions:
            query = query.where(and_(*conditions))

        result = await self.session.execute(query)
        clients = result.scalars().all()

        if distance:
            if not current_user.latitude or not current_user.longitude:
                raise HTTPException(status_code=400, detail="Координаты текущего пользователя не установлены.")
            clients = [
                client for client in clients
                if calculate_distance(current_user.latitude, current_user.longitude,
                                client.latitude, client.longitude) <= distance
            ]

        return clients

    async def create_client(self, request: Request, client_data: ClientCreate) -> Client:
        """Создание нового клиента и сохранение в базе данных."""
        new_client = Client(
            first_name=client_data.first_name,
            last_name=client_data.last_name,
            email=client_data.email,
            gender=client_data.gender,
            avatar=client_data.avatar_url,
        )
        client_ip = self.get_client_ip(request)
        location = await get_location(client_ip)
        new_client.set_latitude(location[0])
        new_client.set_longitude(location[1])

        new_client.set_password(client_data.password)
        self.session.add(new_client)
        await self.session.commit()
        await self.session.refresh(new_client)
        return new_client

    async def check_mutual_match(self, client_id, target_client_id):
        """
        Проверяет, существует ли взаимная симпатия между текущим пользователем и target_client_id.
        """
        query = select(Match).where(
            Match.client_id == target_client_id, Match.target_id == client_id
        )
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
        stmt = select(Match).filter(
            Match.client_id == current_user.id, Match.created_at >= since_time
        )
        result = await self.session.execute(stmt)
        ratings = result.scalars().all()
        return ratings

    @classmethod
    def get_client_ip(cls, request: Request) -> str:
        """
        Функция получает ip из заголовков и возвращает, если localhost, то возвращает случайный ip
        """
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = "89.113.154.158"
        return ip

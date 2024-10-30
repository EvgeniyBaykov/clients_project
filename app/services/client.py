from datetime import datetime, timezone

import jwt
from fastapi import BackgroundTasks, Depends, HTTPException, Request, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import DateTime
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_session
from app.repositories.client import ClientRepository
from app.schemas.client import Client, ClientCreate
from app.services.send_email import send_email_to_user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_client_f(client_data: ClientCreate, session: AsyncSession):
    """
    Создает экземпляр репозитория для работы с клиентами, проверяет существование email,
    сохраняет аватар, если загружен, создаёт нового пользователя через репозиторий.
    """
    client_repo = ClientRepository(session)
    if await client_repo.get_by_email(client_data.email):
        raise HTTPException(status_code=400, detail="Данный email уже используется")

    new_client = await client_repo.create_client(client_data)
    return new_client


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, совпадает ли введенный пароль с хешем в базе данных.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_token(request: Request):
    """
    Декодирует JWT токен из заголовка Authorization.
    """
    auth_header = request.headers.get('authorization')

    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный формат токена",
        )

    token = auth_header[len("Bearer ") :]

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен истек",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
        )


async def get_current_user(
    request: Request, session: AsyncSession = Depends(get_session)
):
    """Функция возвращает текущего пользователя"""
    payload = get_token(request)

    expire = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен истек'
        )

    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Не найден ID пользователя'
        )

    client_repo = ClientRepository(session)
    user = await client_repo.get_by_id(client_id=int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found'
        )

    return user


async def match_client_f(
    target_client_id: int,
    background_tasks: BackgroundTasks,
    current_user: Client,
    session: AsyncSession,
):
    """
    Функция проверяет, существует ли целевой пользователь, создаёт запись об оценке,
    проверяет есть ли взаимная симпатия, если да, то отправляет email обоим пользователям об этом
    """
    client_repo = ClientRepository(session)
    target_client = await client_repo.get_by_id(target_client_id)
    if not target_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Участник не найден"
        )

    has_mutual_match = await client_repo.check_mutual_match(
        current_user.id, target_client_id
    )
    await client_repo.add_match(current_user.id, target_client_id)

    if has_mutual_match:
        await send_email_to_user(
            background_tasks,
            user_name=current_user.first_name,
            user_email=current_user.email,
            target_user_email=target_client.email,
        )
        await send_email_to_user(
            background_tasks,
            user_name=target_client.first_name,
            user_email=target_client.email,
            target_user_email=current_user.email,
        )

        return {
            "message": f"Взаимная симпатия с {target_client.first_name}! Почта: {target_client.email}"
        }

    return {"message": "Симпатия отправлена"}

async def get_clients_f(
    session: AsyncSession,
    gender: str | None,
    first_name: str | None,
    last_name: str | None ,
    created_at: datetime | None
):
    client_repo = ClientRepository(session)
    clients = await client_repo.get_clients(
        gender=gender,
        first_name=first_name,
        last_name=last_name,
        created_at=created_at
    )
    return clients
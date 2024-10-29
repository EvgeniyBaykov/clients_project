from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from jose import jwt
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.client import ClientRepository
from app.schemas.client import ClientCreate
from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_client_f(client_data: ClientCreate,
                          session: AsyncSession):
    """
    Создает экземпляр репозитория для работы с клиентами, проверяет существование email,
    сохраняет аватар, если загружен, создаёт нового пользователя через репозиторий.
    """
    client_repo = ClientRepository(session)
    if await client_repo.get_by_email(client_data.email):
        raise HTTPException(status_code=400, detail="Данный email уже используется")

    new_client = await client_repo.create_client(client_data)
    return new_client


def create_access_token(data: dict) -> str:
    """Создание JWT токена с заданными данными и сроком действия."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encode_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, совпадает ли введенный пароль с хешем в базе данных.
    """
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(session:AsyncSession, email: EmailStr, password: str):
    """Проверяет, существует ли пользователь с указанным email, и совпадает ли его пароль."""
    client_repo = ClientRepository(session)
    user = await client_repo.get_by_email(email=email)
    if not user or verify_password(plain_password=password, hashed_password=user.hashed_password) is False:
        return None
    return user

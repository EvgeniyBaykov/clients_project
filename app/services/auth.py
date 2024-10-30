from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.client import ClientRepository
from app.schemas.auth import UserAuth
from app.core.config import settings
from app.services.client import verify_password


def create_access_token(user_id: int) -> str:
    """Создание JWT токена с заданными данными и сроком действия."""
    to_encode = {"sub": str(user_id)}
    expire = datetime.now(timezone.utc) + timedelta(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encode_jwt


async def authenticate_user(session: AsyncSession, email: EmailStr, password: str):
    """Проверяет, существует ли пользователь с указанным email, и совпадает ли его пароль."""
    client_repo = ClientRepository(session)
    user = await client_repo.get_by_email(email=email)
    if not user or verify_password(plain_password=password, hashed_password=user.hashed_password) is False:
        return None
    return user


async def auth_user_f(user_data: UserAuth, session: AsyncSession):
    """
    Авторизует пользователя, возвращает токен
    """
    user = await authenticate_user(session=session, email=user_data.email, password=user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверная почта или пароль')
    access_token = create_access_token(user.id)

    return {'access_token': access_token}

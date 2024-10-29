from datetime import datetime, timezone
from fastapi import Depends, HTTPException, Request, status
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.db.session import get_session
from app.repositories.client import ClientRepository
from app.schemas.client import ClientCreate

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


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, совпадает ли введенный пароль с хешем в базе данных.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_token(request: Request):
    token = request.cookies.get('access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')
    return token


async def get_current_user(session: AsyncSession = Depends(get_session), token: str = Depends(get_token)):
    """Функция возвращает текущего пользователя"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не валидный!')

    expire = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен истек')

    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не найден ID пользователя')

    client_repo = ClientRepository(session)
    user = await client_repo.get_by_id(client_id=int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')

    return user


async def match_client_f():
    pass

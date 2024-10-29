from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.schemas.client import Client, ClientCreate
from app.schemas.auth import UserAuth, Token
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.services.client import create_client_f, create_access_token, authenticate_user

router = APIRouter()


@router.post("/api/clients/create", response_model=Client, status_code=201)
async def create_client(client_data: ClientCreate,
                        session: AsyncSession = Depends(get_session)):
    """Endpoint для регистрации пользователя"""
    return await create_client_f(client_data, session)


@router.post("/api/clients/login/", response_model=Token)
async def auth_user(response: Response, user_data: UserAuth, session: AsyncSession = Depends(get_session)):
    """Endpoint для авторизации пользователя"""
    user = await authenticate_user(session=session, email=user_data.email, password=user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверная почта или пароль')
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {'access_token': access_token}


@router.post("/logout/")
async def logout_user(response: Response):
    """Endpoint для выхода пользователя"""
    response.delete_cookie(key="access_token")
    return {'message': 'Пользователь успешно вышел из системы'}

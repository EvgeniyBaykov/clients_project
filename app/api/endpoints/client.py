from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.client import Client, ClientCreate
from app.schemas.auth import UserAuth, Token
from app.db.session import get_session
from app.services.auth import auth_user_f
from app.services.client import create_client_f, get_current_user
from app.repositories.client import ClientRepository

router = APIRouter()


@router.post("/api/clients/create", response_model=Client, status_code=201)
async def create_client(client_data: ClientCreate,
                        session: AsyncSession = Depends(get_session)):
    """Endpoint для регистрации пользователя"""
    return await create_client_f(client_data, session)


@router.post("/api/clients/login/", response_model=Token)
async def auth_user(response: Response, user_data: UserAuth, session: AsyncSession = Depends(get_session)):
    """Endpoint для авторизации пользователя"""
    return await auth_user_f(response, user_data, session)


@router.post("/logout/")
async def logout_user(response: Response):
    """Endpoint для выхода пользователя"""
    response.delete_cookie(key="access_token")
    return {'message': 'Пользователь успешно вышел из системы'}


@router.post("/api/clients/{target_client_id}/match", response_model=dict)
async def match_client(
        target_client_id: int,
        current_user: Client  = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
):
    client_repo = ClientRepository(session)

    # Проверяем, существует ли оцениваемый пользователь
    target_client = await client_repo.get_by_id(target_client_id)
    if not target_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Участник не найден")

    # Проверка взаимной симпатии
    has_mutual_match = await client_repo.check_mutual_match(current_user.id, target_client_id)

    if has_mutual_match:
        # Отправляем уведомления по email
        # await send_match_email(client.email, target_client.first_name, target_client.email)
        # await send_match_email(target_client.email, client.first_name, client.email)

        return {"message": f"Взаимная симпатия с {target_client.first_name}! Почта: {target_client.email}"}

    # Добавляем симпатию, если не было взаимной
    await client_repo.add_match(current_user.id, target_client_id)

    return {"message": "Симпатия отправлена"}

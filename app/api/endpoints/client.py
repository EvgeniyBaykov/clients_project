from datetime import datetime
from typing import Sequence

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.middlwares.rate_limit import rate_limit
from app.db.session import get_session
from app.schemas.auth import Token, UserAuth
from app.schemas.client import Client, ClientCreate
from app.services.auth import auth_user_f, refresh_access_token
from app.services.client import (
    create_client_f,
    get_clients_f,
    get_current_user,
    match_client_f,
)

router = APIRouter()


@router.post("/api/clients/create", response_model=Client, status_code=201)
async def create_client(
    request: Request,
    client_data: ClientCreate,
    session: AsyncSession = Depends(get_session),
):
    """Endpoint для регистрации пользователя"""
    return await create_client_f(request, client_data, session)


@router.post("/api/clients/login/", response_model=Token)
async def auth_user(
    user_data: UserAuth,
    session: AsyncSession = Depends(get_session),
):
    """Endpoint для авторизации пользователя"""
    return await auth_user_f(user_data, session)


@router.post("/api/clients/logout/")
async def logout_user():
    """Endpoint для выхода пользователя"""
    return {'message': 'Пользователь успешно вышел из системы'}


@router.post(
    "/api/clients/{target_client_id}/match",
    response_model=dict,
    dependencies=[Depends(HTTPBearer())],
)
async def match_client(
    target_client_id: int,
    background_tasks: BackgroundTasks,
    current_user: Client = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    rate_limit: None = Depends(rate_limit),
):
    """Endpoint оценивания участником другого участника"""
    return await match_client_f(
        target_client_id, background_tasks, current_user, session
    )


@router.get(
    "/api/list", response_model=Sequence[Client], dependencies=[Depends(HTTPBearer())]
)
async def get_clients(
    session: AsyncSession = Depends(get_session),
    current_user: Client = Depends(get_current_user),
    gender: str | None = Query(None, description="Фильтр по полу"),
    first_name: str | None = Query(None, description="Фильтр по имени"),
    last_name: str | None = Query(None, description="Фильтр по фамилии"),
    distance: float | None = Query(None, description="Фильтр по расстоянию (км)"),
    created_at: datetime | None = Query(None, description="Фильтр по дате регистрации"),
):
    """Endpoint для получения списка участников"""
    return await get_clients_f(
        session, current_user, gender, first_name, last_name, distance, created_at
    )

@router.post("/api/token/refresh")
def refresh_token_endpoint(refresh_token: str):
    """
    Эндпоинт для обновления access токена с использованием refresh токена.
    """
    return refresh_access_token(refresh_token)

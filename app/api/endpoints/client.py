from fastapi import APIRouter, Depends, UploadFile, File
from app.schemas.client import Client, ClientCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.services.client import create_client_f

router = APIRouter()


@router.post("/api/clients/create", response_model=Client, status_code=201)
async def create_client(client_data: ClientCreate,
                        session: AsyncSession = Depends(get_session)):
    """Endpoint для регистрации пользователя"""
    return await create_client_f(client_data, session)

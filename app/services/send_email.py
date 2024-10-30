from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS
)


async def send_email_to_user(background_tasks: BackgroundTasks,
                             user_name:str,
                             user_email: str,
                             target_user_email: str):
    """Функция для отправки письма пользователю"""
    message_text = f"Вы понравились {user_name}! Почта участника: {user_email}"
    message = MessageSchema(
        subject="У вас взаимная симпатия!",
        recipients=[target_user_email],
        body=message_text,
        subtype=MessageType.plain,
    )
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message, template_name=None)

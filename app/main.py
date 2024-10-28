from fastapi import FastAPI
from app.api.endpoints import client


app = FastAPI()

app.include_router(client.router, tags=["clients"])

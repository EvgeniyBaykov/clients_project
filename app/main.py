from fastapi import FastAPI
from app.api.endpoints import client, storage


app = FastAPI()

app.include_router(client.router, tags=["clients"])
app.include_router(storage.router, tags=["storage"])


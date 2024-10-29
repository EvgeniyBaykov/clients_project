from pydantic import BaseModel


class Client(BaseModel):
    id: int
    client_id: int
    target_id: int


    class Config:
        from_attributes = True
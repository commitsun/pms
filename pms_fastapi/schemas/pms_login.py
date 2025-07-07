from pydantic import BaseModel


class PmsLoginInput(BaseModel):
    username: str
    password: str

from pydantic import BaseModel


class PropertyId(BaseModel):
    id: int
    name: str

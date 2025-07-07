from pydantic import BaseModel


class Language(BaseModel):
    id: int
    name: str
    isoCode: str

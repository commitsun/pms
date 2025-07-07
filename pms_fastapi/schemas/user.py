from pydantic import AnyHttpUrl, BaseModel

from .property import PropertyId


class User(BaseModel):
    id: int
    name: str
    firstname: str = ""
    lastname: str = ""
    lastname2: str = ""
    email: str = ""
    phone: str = ""
    image: AnyHttpUrl = ""
    defaultProperty: PropertyId

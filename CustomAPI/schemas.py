from pydantic import BaseModel


class API(BaseModel):
    id: int
    name: str
    data: str
    channel: str

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int
    name: str
    password: str

    class Config:
        orm_mode = True


class Logins(BaseModel):
    user_id: int
    session_id: str

    class Config:
        orm_mode = True


class Owners(BaseModel):
    user_id: int
    api_id: int

    class Config:
        orm_mode = True


class Editors(BaseModel):
    user_id: int
    api_id: int

    class Config:
        orm_mode = True




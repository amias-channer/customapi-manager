from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column


from .database import Base


class Api(Base):
    __tablename__ = "apis"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    data = Column(String, index=True)
    channel = Column(String, index=True, default="")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    password = Column(String, index=True)
    admin = Column(Boolean, index=True)
    enabled = Column(Boolean, index=True)


class Login(Base):
    __tablename__ = "logins"
    user_id = Column(Integer, index=True)
    session_id = Column(String, primary_key=True, index=True)


class Owner(Base):
    __tablename__ = "owners"
    user_id = Column(Integer, index=True)
    api_id = Column(Integer, primary_key=True, index=True)


class Editor(Base):
    __tablename__ = "editors"
    user_id = Column(Integer, index=True)
    api_id = Column(Integer, primary_key=True, index=True)

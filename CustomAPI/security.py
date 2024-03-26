from typing import Annotated
from fastapi import HTTPException, FastAPI, Response, Request, Depends, Header, APIRouter, status, Form, security
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPAuthorizationCredentials
from uuid import UUID, uuid4
from fastapi import APIRouter
import CustomAPI

backend = CustomAPI.Backend()
security = HTTPBasic()


def authenticate_user(request: Request, response: Response,
                      credentials: HTTPBasicCredentials = Depends(security)) -> CustomAPI.Login or False:
    session_id = request.cookies.get("session_id")
    login = backend.login(credentials.username, credentials.password, session_id=session_id)
    if not login:
        credentials.username = None
        credentials.password = None
        response.set_cookie("session_id", "")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"Authorization": "Basic"},
        )
    else:
        response.set_cookie("session_id", login.session_id)
        return login


def get_authenticated_user_from_session_id(request: Request):
    session_id = request.cookies.get("session_id")
    user = backend.get_session_user(session_id)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid session ID",
        )
    return user


def is_admin_user(request: Request):
    user = get_authenticated_user_from_session_id(request)
    if not user.name == "amias":
        raise HTTPException(status_code=403, detail="Forbidden")
    return user

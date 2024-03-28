from typing import Annotated
from fastapi import HTTPException, FastAPI, Response, Request, Depends, Header, APIRouter, status, Form, security
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPAuthorizationCredentials
from uuid import UUID, uuid4
from fastapi import APIRouter
import CustomAPI

backend = CustomAPI.Backend()
security = HTTPBasic()


async def authenticate_user(request: Request, response: Response,
                      credentials: HTTPBasicCredentials = Depends(security)) -> CustomAPI.User or False:
    session_id = request.cookies.get("session_id")
    login = await backend.login(credentials.username, credentials.password, session_id=session_id)
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
        return await backend.fetch_user(login.user_id)


async def logout_user(request: Request):
    session_id = request.cookies.get("session_id")
    if await backend.logout(session_id):
        response = RedirectResponse("/wipe_session")
        response.headers["Authorization"] = "Basic"
        response.set_cookie("session_id", "")
        return response
    else:
        raise HTTPException(
            status_code=500,
            detail="Logout failed",
        )


async def is_loggedin_user(request: Request):
    session_id = request.cookies.get("session_id")
    user = await backend.get_session_user(session_id)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid session ID",
            headers={"Authorization": "Basic"},
        )
    return user


async def is_admin_user(request: Request):
    user = await is_loggedin_user(request)
    if not user.admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user

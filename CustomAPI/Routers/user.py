from typing import Annotated
from fastapi import HTTPException, FastAPI, Response, Request, Depends, Header, APIRouter, status, Form, security
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPAuthorizationCredentials
from uuid import UUID, uuid4
from fastapi import APIRouter
import CustomAPI

from CustomAPI.template import head, foot, loginform


router = APIRouter()

backend = CustomAPI.Backend()


@router.get("/admin", response_class=HTMLResponse)
def admin(session: CustomAPI.Login = Depends(CustomAPI.security.is_admin_user)):
    output = """ <form method="get">
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <button type="submit" formaction="/user/delete">Delete</button>
    <select name='id'>"""
    for user in backend.fetch_user_list():
        output += """<option value="{0}">{1}</option>""".format(user.id, user.name)
    output += """
    </select>
    <button type="submit" formaction="/user/edit">Edit</button>    
    </form>
    <br><br>
    <form method="post" action="/user/create">
    <table>
    <tr><td>User Name</td><td><input name="name"></td></tr>
    <tr><td>Password</td><td><input name="password"></td></tr>
    <tr><td colspan="2"><input type="submit" value="Create User"></td></tr>
    </table>
    </form>
    <br><br>
    <table>
    """
    for login in backend.fetch_login_list():
        name = backend.get_user_name(login.user_id)
        output += "<tr><td>{}</td><td>{}</td></tr>".format(name, login.session_id)
    output += "</table><br><br>"
    return HTMLResponse(status_code=200, content=head + output + foot)


@router.get("/user/edit", response_class=HTMLResponse)
def edit_user(id: int, session: CustomAPI.Login = Depends(CustomAPI.security.is_admin_user)):
    user = backend.fetch_user(id)
    output = f"""
    <form action="/user/edit" method="post">
    <table>
    <tr><td>User Name</td><td><input name="name" value="{user.name}"></td></tr>
    <tr><td>Password</td><td><input name="password" value="{user.password}"></td></tr>
    <tr><td>Enabled</td><td>"""
    if user.enabled:
        output += """<input type="radio"" id="enabled" value="True" checked /><input type="radio"" id="enabled" value="False" />"""
    else:
        output += """<input type="radio"" id="enabled" value="True" /><input type="radio"" id="enabled" value="False" checked />"""
    output += """</td></tr><tr><td><input type="hidden" name="id" value="{user.id}"></td></tr>
    <tr><td colspan="2" align="center"><input type="submit" value="Edit"></td></tr>
    </table>
    </form>
    <br><br>
    <form method="get" action="/api/edit">
    <select name='id'>"""
    for relation in backend.fetch_api_list(id):
        api = backend.fetch_api(relation.api_id)
        output += """<option value="{0}">{1}</option>""".format(api.id, api.name)
    output += """<input type="submit" value="edit"></select></form><br><br>
    """
    return HTMLResponse(status_code=200, content=head + output + foot)


@router.post("/user/edit", response_model=None)
def edit_user(id: Annotated[int, Form()], name: Annotated[str, Form()] or None, password: Annotated[str, Form()],
              session: CustomAPI.Login = Depends(CustomAPI.security.is_admin_user)):
    if backend.edit_user(id, name, password):
        return HTMLResponse(status_code=200, content=head + "Edited {0} successfully <br> {1}".format(name, foot))
    else:
        return HTTPException(status_code=500, detail="Internal server error")


@router.post("/user/create", response_model=None)
async def user_create(name: Annotated[str, Form()], password: Annotated[str, Form()],
                      session: CustomAPI.Login = Depends(CustomAPI.security.is_admin_user)):
    if await backend.create_user(name, password):
        return HTMLResponse(status_code=200,
                            content=head + "<br><br> Created {0} successfully <br><br><br> {1}".format(name, foot))
    else:
        return HTTPException(status_code=500, detail="Internal server error")


@router.get("/user/delete", response_model=None)
async def user_delete(id: int, session: CustomAPI.Login = Depends(CustomAPI.security.is_admin_user)):
    if id == session.id:
        return HTTPException(status_code=403, detail="Forbidden")

    if await backend.delete_user(id):
        return HTMLResponse(status_code=200,
                            content=head + "<br><br> Deleted {0} successfully <br><br><br> {1}".format(id, foot))
    else:
        return HTTPException(status_code=404, detail="Item not found")


@router.get("/whoami", response_class=HTMLResponse)
async def whoami(user: CustomAPI.Login = Depends(CustomAPI.security.get_authenticated_user_from_session_id)):
    return backend.get_user_name(user.id)


@router.get("/wipe_session", response_class=HTMLResponse)
async def wipe_session(response: Response):
    response.set_cookie("session_id", "")
    response.headers["Authorization"] = "None"
    return head + "Session wiped <a href='/'>Login</a>"


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request, response: Response, credentials: Annotated[HTTPBasicCredentials, Depends(HTTPBasic)],
                 session: CustomAPI.Login = Depends(CustomAPI.security.get_authenticated_user_from_session_id)):
    session_id = request.cookies.get("session_id")
    if backend.logout(session_id):
        credentials.username = None
        credentials.password = None
        response.set_cookie("session_id", "")
        response.headers["Authorization"] = "None"
        return HTMLResponse(content=head + "Logging out <br><br> <a href='/wipe_session'>Continue</a>",
                            headers=response.headers)
    else:
        return head + "Error logging out" + foot
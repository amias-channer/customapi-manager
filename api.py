from typing import Annotated
from fastapi import HTTPException, FastAPI, Response, Request, Depends, Header, APIRouter, status, Form, security
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPAuthorizationCredentials
from uuid import UUID, uuid4

import CustomAPI
import json
import random

app = FastAPI()
backend = CustomAPI.Backend()
security = HTTPBasic()


head = """
<html>
<head>
<style>
body {
  font-family: helvetica, sans-serif;
}
</style>
<body>
<h1>CustomAPI</h1>
<p>CustomAPI system for providing data for streamelements customapi commands</p>
"""
loginform = """
<form action='/start' method=''>
    <!-- input name='username'><br>
    <input type= 'password' name='password'><br -->
    <input type='submit' value='Login'>
</form>"""
foot = """ -  <a href="/logout">Logout</a>  -  <a href="/start">Menu</a>  - </body></html>"""


def api_form(action, method, id, name, data, channel):
    form = """
    <form action="/api/{0}" method="{5}">
    <input type="hidden" name="id" value="{1}">
    <table>
    <tr><td>API Name </td><td><input name="name" value="{2}"></td></tr>
    <tr><td>API Data </td><td><textarea name="data">{3}</textarea></td></tr>
    <tr><td>Channel</td><td><input name="channel" value="{4}"></td></tr>
    <tr><td colspan="2" align="center"><input type="submit" value="{0}"></td></tr>
    </table></form>""".format(action, id, name, data, channel, method)
    return form


def generate_link_to_api(api_id, channel):
    tricky_string = '${customapi.se.amias.net'
    end_bracket = '}'
    return "{0}/api/{1}/{2}{3}".format(tricky_string, api_id, channel, end_bracket)


def authenticate_user(request: Request, response: Response, credentials: HTTPBasicCredentials = Depends(security)) -> CustomAPI.Login or False:
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


@app.get("/", response_class=HTMLResponse)
async def root():
    return head + loginform


@app.get("/start", response_class=HTMLResponse)
async def start(user: CustomAPI.Login = Depends(authenticate_user)):
    banner = "<h3>Welcome {}</h3>".format(backend.get_user_name(user.user_id))
    apilist = """<form method="post" action="/api/edit">"""
    apilist += """<button type="submit" formaction="/api/delete">Delete</button>"""
    optlist = "<select name='id'>"
    for relation in backend.fetch_api_list(user.user_id):
        api = backend.fetch_api(relation.api_id)
        optlist += """<option value="{0}">{1}</option>""".format(api.id, api.name)
    optlist += "</select>"
    apilist += optlist
    apilist += """<button type="submit" formaction="/api/edit">Edit</button>"""
    apilist += "</form>"
    createform = api_form("create", "post", 0, "", "", "")
    return head + banner + apilist + createform + foot


@app.get("/whoami", response_class=HTMLResponse)
async def whoami(user: CustomAPI.Login = Depends(get_authenticated_user_from_session_id)):
    return backend.get_user_name(user.id)


@app.get("/wipe_session", response_class=HTMLResponse)
async def wipe_session(response: Response):
    response.set_cookie("session_id", "")
    response.headers["Authorization"] = "None"
    return head + "Session wiped <a href='/'>Login</a>"


@app.get("/logout", response_class=HTMLResponse)
async def logout(request: Request, response: Response, credentials: Annotated[HTTPBasicCredentials, Depends(security)], session: CustomAPI.Login = Depends(get_authenticated_user_from_session_id)):
    session_id = request.cookies.get("session_id")
    if backend.logout(session_id):
        credentials.username = None
        credentials.password = None
        response.set_cookie("session_id", "")
        response.headers["Authorization"] = "None"
        return HTMLResponse(content=head + "Logging out <br><br> <a href='/wipe_session'>Continue</a>", headers=response.headers)
    else:
        return head + "Error logging out" + foot


@app.post("/api/create", response_class=HTMLResponse)
async def api_create(name: Annotated[str, Form()], data: Annotated[str, Form()], channel: Annotated[str, Form()], login: CustomAPI.Login = Depends(get_authenticated_user_from_session_id)):
    # name: str, data: str, channel: str,
    api_id = await backend.create_api(name, data, channel, login.id)
    if api_id:
        se_command = generate_link_to_api(api_id, channel)
        return HTMLResponse(status_code=200, content="created {0} successfully <br><br> {1} <br><br> {2}".format(api_id, se_command, foot))
    else:
        return HTMLResponse(status_code=201, detail=head + "Error making api" + foot)


@app.get("/api/edit", response_class=HTMLResponse)
async def api_edit(id: int, session: CustomAPI.Login = Depends(get_authenticated_user_from_session_id)):
    if not backend.is_owner(session.id, id):
        return HTMLResponse(status_code=403, content="Forbidden")

    api = backend.fetch_api(id)
    editform = api_form("edit", "post", api.id, api.name, api.data, api.channel)
    return HTMLResponse(status_code=200, content=head + editform + foot)


@app.post("/api/edit", response_class=HTMLResponse)
async def api_edit(id: Annotated[int, Form()], name: Annotated[str, Form()] or None, data: Annotated[str, Form()] or None, channel: Annotated[str, Form()] or None, session: CustomAPI.Login = Depends(get_authenticated_user_from_session_id)):
    if id and not data and not name and not channel:
        return RedirectResponse(url="/api/edit/{0}".format(id))

    # id: int,  name: str or None, data: str or None, channel: str or None,
    if await backend.edit_api(id, name, data, channel):
        return HTMLResponse(status_code=200, content="edited {0} successfully <br> {1}".format(id, foot))
    else:
        return HTMLResponse(status_code=201, content=head + 'EDIT ERROR' + foot)


@app.post("/api/delete", response_class=HTMLResponse)
async def api_delete(id: Annotated[int, Form()], session: CustomAPI.Login = Depends(get_authenticated_user_from_session_id)):
    if not backend.is_owner(session.id, id):
        return HTMLResponse(status_code=403, content="Forbidden")

    if await backend.delete_api(id):
        return HTMLResponse(status_code=200, content="Deleted {0} successfully <br> {1}".format(id, foot))
    else:
        return HTMLResponse(status_code=404, content="Item not found")


@app.get("/api/{i}/{c}", response_model=None)
def api(i: int, c: str, r: int or None = None,
        user_agent: str | None = Header(default=None),
        http_x_streamelements_channel: str | None = Header(default=None)):

    # check headers
    allowed_user_agents = ['StreamElements Bot',
                           'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36']
    if user_agent not in allowed_user_agents:
        return HTMLResponse(status_code=403, content="Forbidden user agent")

    #if http_x_streamelements_channel != c:
    #    return HTMLResponse(status_code=403, content="Incorrect Headers")

    data = backend.fetch_api_data(i, c)
    if data:
        if r == 1:
            return random.choice(data.split(","))
        return data
    else:
        return HTTPException(status_code=404, detail="Item not found")


@app.post("/user/create", response_model=None)
async def user_create(name: str, password: str, session: CustomAPI.Login = Depends(get_authenticated_user_from_session_id)):
    if await backend.create_user(name, password):
        return {"message": "created successfully"}
    else:
        return HTTPException(status_code=500, detail="Internal server error")


@app.post("/user/delete", response_model=None)
async def user_delete(id: int, session: CustomAPI.Login = Depends(get_authenticated_user_from_session_id)):
    if id == session.user_id:
        return HTTPException(status_code=403, detail="Forbidden")

    if await backend.delete_user(id):
        return {"message": "deleted successfully"}
    else:
        return HTTPException(status_code=404, detail="Item not found")

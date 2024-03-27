from typing import Annotated
from fastapi import HTTPException, FastAPI, Response, Request, Depends, APIRouter, status, Form, security
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPAuthorizationCredentials
from uuid import UUID, uuid4

import CustomAPI
import json
import random

router = APIRouter()

backend = CustomAPI.Backend()
security = HTTPBasic()


def api_form(action, method, id, name, data, channel, editor):
    form = """
    <form action="/api/{0}" method="{5}">
    <input type="hidden" name="id" value="{1}">
    <table>
    <tr><td align="right">Name</td><td><input size="20" name="name" value="{2}">

    </td></tr>
    <tr><td align="right">Data</td><td><textarea id="data" cols="43" rows="10" name="data">{3}</textarea></td></tr>
    <tr><td align="right">Channel</td><td><input size="20" id="channel" name="channel" value="{4}">
    <button type="button" onclick="clearChannel()" title="Add a channel name to make this API available to only one channel,
     or click X to leave it open and get shorter link">X</button> 
    <span align="right">
    <button type="button" onclick="crToComma();return False" title="Replace the lines in the data with Commas">L</button>
    <button type="button" onclick="spacesToComma()" title="Replace the spaces in the data with Commas">S</button>
    <button type="button" onclick="noDupes()" title="Remove duplicated punctation">D</button>
    <button type="button" onclick="noSingleQuotes()" title="Remove Single quotes from the data">'</button>
    <button type="button" onclick="noDoubleQuotes()" title="Remove Double quotes from the data">"</button>
    </span>
     <td></tr>
    <tr><td align="right">Shared With</td><td><select name='editor'><option value="0">Nobody</option>""".format(action, id, name, data, channel, method)
    for user in backend.fetch_user_list():
        if user.id == editor:
            form += """<option value="{0}" selected>{1}</option>""".format(user.id, user.name)
        else:
            form += """<option value="{0}">{1}</option>""".format(user.id, user.name)
    form += "</select></td></tr></td></tr><tr><td colspan='2' align='left'><br><input type='submit'></td><tr></table></form>"
    return form


def generate_link_to_api(api_id, channel) -> str:

    opening_string = '${customapi.api.amias.net'
    closing_string = '}'
    cout = ""
    if channel:
        cout += "?c=" + channel
    out = """{0}/{1}{2}{3}""".format(opening_string, api_id, cout, closing_string)
    api = backend.fetch_api(api_id)

    return out


@router.post("/api/create", response_class=HTMLResponse)
async def api_create(name: Annotated[str, Form()], data: Annotated[str, Form()],
                     channel: Annotated[str, Form()], editor: Annotated[int, Form()],
                     login: CustomAPI.Login = Depends(CustomAPI.security.get_authenticated_user_from_session_id)
                     ):
    # name: str, data: str, channel: str,
    api_id = await backend.create_api(name, data, channel, login.id, editor)
    if api_id:
        se_command = generate_link_to_api(api_id, channel)
        out = "created {0} successfully <br><br> {1} <br><br>".format(api_id, se_command)
        return HTMLResponse(status_code=200,
                            content=CustomAPI.template.head + out + CustomAPI.template.foot)
    else:
        return HTMLResponse(status_code=201, content=CustomAPI.template.head + "Error making api" + CustomAPI.template.foot)


@router.get("/api/edit", response_class=HTMLResponse)
async def api_edit(id: int, session: CustomAPI.Login = Depends(CustomAPI.security.get_authenticated_user_from_session_id)):
    owner_id = backend.is_owner(session.id, id)
    editor = backend.fetch_editor(id)

    if not owner_id == session.id:
        if editor and not editor.user_id == session.id:
            return HTMLResponse(status_code=403, content="Forbidden")

    api = backend.fetch_api(id)
    link = '<font size="-1"><br>' + generate_link_to_api(api.id, api.channel) + "<br></font>"
    if editor:
        editor_id = editor.user_id
    else:
        editor_id = 0
    # the default value in the form is space because the form will send a None if its truly empty.
    if api.channel == '':
        api.channel = ' '
    editform = api_form("edit", "post", api.id, api.name, api.data, api.channel, editor_id)
    editform = "<br>" + editform
    return HTMLResponse(status_code=200, content=CustomAPI.template.head + editform + link + CustomAPI.template.foot)


@router.post("/api/edit", response_class=HTMLResponse)
async def api_edit(id: Annotated[int, Form()], name: Annotated[str, Form()],
                   data: Annotated[str, Form()], channel: Annotated[str, Form()],
                   editor: Annotated[int, Form()],
                   session: CustomAPI.Login = Depends(CustomAPI.security.get_authenticated_user_from_session_id)):
    # if id and not data and not name and not channel:
    #    return RedirectResponse(url="/api/edit/{0}".format(id))
    if not backend.is_owner(session.id, id) and not backend.is_editor(session.id, id):
        return HTMLResponse(status_code=403, content="Forbidden")
    # id: int,  name: str or None, data: str or None, channel: str or None,
    if channel == ' ':
        channel = ''
    if backend.edit_api(id, name, data, channel, editor):
        link = generate_link_to_api(id, channel)
        ret = """<br> <a href="/api/edit?id={0}">edit</a>ed <a href="/{0}">{0}</a> successfully <br><br> {1} <br><br> """.format(id, link)
        return HTMLResponse(status_code=200, content=CustomAPI.template.head + ret + CustomAPI.template.foot)
    else:
        return HTMLResponse(status_code=201, content=CustomAPI.template.head + 'EDIT ERROR' + CustomAPI.template.foot)


@router.get("/api/delete", response_class=HTMLResponse)
async def api_delete(id: int, session: CustomAPI.Login = Depends(CustomAPI.security.get_authenticated_user_from_session_id)):
    if not backend.is_owner(session.id, id):
        return HTMLResponse(status_code=403, content="Forbidden")

    if await backend.delete_api(id):
        return HTMLResponse(status_code=200, content="{0} Deleted {1} successfully <br> {2}".format(CustomAPI.template.head, id, CustomAPI.template.foot))
    else:
        return HTMLResponse(status_code=404, content="Item not found")


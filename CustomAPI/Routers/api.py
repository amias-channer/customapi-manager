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
    <span align="right">
    <button type="button" onclick="crToComma();return False" title="Replace the lines in the data with Commas">L</button>
    <button type="button" onclick="spacesToComma()" title="Replace the spaces in the data with Commas">S</button>
    <button type="button" onclick="noDupes()" title="Remove duplicated punctation">D</button>
    <button type="button" onclick="noSingleQuotes()" title="Remove Single quotes from the data">'</button>
    <button type="button" onclick="noDoubleQuotes()" title="Remove Double quotes from the data">"</button>
    </span>
    </td></tr>
    <tr><td align="right">Data</td><td><textarea id="data" cols="27" name="data">{3}</textarea></td></tr>
    <tr><td align="right">Channel</td><td><input size="20" name="channel" value="{4}">
    <span align="right">
    <select name='editor'><option value="0">Select Editor</option>""".format(action, id, name, data, channel, method)
    for user in backend.fetch_user_list():
        if user.id == editor:
            form += """<option value="{0}" selected>{1}</option>""".format(user.id, user.name)
        else:
            form += """<option value="{0}">{1}</option>""".format(user.id, user.name)
    form += "</select><span></td></tr></td></tr><tr><td colspan='2' align='center'><input type='submit'></td><tr></table></form>"
    return form


def generate_link_to_api(api_id, channel):
    tricky_string = '${customapi.api.amias.net'
    end_bracket = '}'
    return "{0}/a/{1}/{2}{3}".format(tricky_string, api_id, channel, end_bracket)


@router.post("/api/create", response_class=HTMLResponse)
async def api_create(name: Annotated[str, Form()], data: Annotated[str, Form()], channel: Annotated[str, Form()],
                     editor: Annotated[int, Form()],
                     login: CustomAPI.Login = Depends(CustomAPI.security.get_authenticated_user_from_session_id)):
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
        if editor and not editor.id == session.id:
            return HTMLResponse(status_code=403, content="Forbidden")

    api = backend.fetch_api(id)
    link = '<font size="-1"><br>' + generate_link_to_api(api.id, api.channel) + "<br></font>"
    if editor:
        editor_id = editor.user_id
    else:
        editor_id = 0
    editform = api_form("edit", "post", api.id, api.name, api.data, api.channel, editor_id)
    editform = "<br>" + editform
    return HTMLResponse(status_code=200, content=CustomAPI.template.head + editform + link + CustomAPI.template.foot)


@router.post("/api/edit", response_class=HTMLResponse)
async def api_edit(id: Annotated[int, Form()], name: Annotated[str, Form()] or None,
                   data: Annotated[str, Form()] or None, channel: Annotated[str, Form()] or None,
                   editor: Annotated[int, Form()] or None,
                   session: CustomAPI.Login = Depends(CustomAPI.security.get_authenticated_user_from_session_id)):
    # if id and not data and not name and not channel:
    #    return RedirectResponse(url="/api/edit/{0}".format(id))
    if not backend.is_owner(session.id, id) and not backend.is_editor(session.id, id):
        return HTMLResponse(status_code=403, content="Forbidden")
    # id: int,  name: str or None, data: str or None, channel: str or None,
    if backend.edit_api(id, name, data, channel, editor):
        link = generate_link_to_api(id, channel)
        return HTMLResponse(status_code=200,
                            content="{0} edited {1} successfully <br><br> {2} <br><br> {3}".format(CustomAPI.template.head, id, link,
                                                                                                   CustomAPI.template.foot))
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


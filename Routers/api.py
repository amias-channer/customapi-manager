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


async def api_form(action, method, id, name, data, channel, editor, delimiter=','):
    if channel == '':
        channel = ' '
    regex = '\\r\\n|\\n|\\r'

    form = """
    <form action="/api/{0}" method="{5}">
    <input type="hidden" name="id" value="{1}">
    <table>
    <tr><td align="right">Name</td><td><input size="38" name="name" value="{2}"></td></tr>
    <tr><td colspan="2"><textarea id="data" cols="56" rows="10" name="data">{3}</textarea></td></tr>
    <tr><td align="right">&nbsp;&nbsp;Delimiter</td><td><input id="delimiter" name="delimiter" size="20" value="{7}">
    <font size="-3">
    <button type="button" onclick="crToDelimiter()";return false" title="Replace the lines in the data with Commas">L</button>
    <button type="button" onclick="spacesToDelimiter()" title="Replace the spaces in the data with Commas">S</button>&nbsp;&nbsp;
    <button type="button" onclick="noDupes()" title="Remove duplicated punctuation">D</button>
    <button type="button" onclick="noSingleQuotes()" title="Remove Single quotes from the data">'</button>
    <button type="button" onclick="noDoubleQuotes()" title="Remove Double quotes from the data">"</button>
    </font>
     <td></tr>
    <tr><td align="right">Channel</td><td><input size="17" id="channel" name="channel" value="{4}">    
    <button type="button" onclick="clearChannel()" title="Add a channel name to make this API available to only one channel,
     or click X to leave it open and get shorter link">X</button></td><tr>
    <tr><td align="right">Editor</td><td><select name='editor'><option value="0">Nobody</option>"""\
        .format(action, id, name, data, channel, method, regex, delimiter)
    for user in await backend.fetch_user_list():
        if user.id == editor:
            form += """<option value="{0}" selected>{1}</option>""".format(user.id, user.name)
        else:
            form += """<option value="{0}">{1}</option>""".format(user.id, user.name)
    form += """</select></td></tr>
    <tr><td>&nbsp;</td><td><br><input type='submit'></td><tr></table></form>""".format(delimiter)
    return form


async def generate_link_to_api(api_id, channel) -> str:

    opening_string = '${customapi.api.amias.net'
    closing_string = '}'
    cout = ""
    if channel:
        cout += "?c=" + channel
    out = """{0}/{1}{2}{3}""".format(opening_string, api_id, cout, closing_string)
    return out


@router.post("/api/create", response_class=HTMLResponse)
async def api_create(name: Annotated[str, Form()], data: Annotated[str, Form()],
                     channel: Annotated[str, Form()], editor: Annotated[int, Form()], delimiter: Annotated[str, Form()],
                     user: CustomAPI.User = Depends(CustomAPI.security.is_loggedin_user)
                     ):
    if channel == ' ':
        channel = ''
    # name: str, data: str, channel: str,
    api_id = await backend.create_api(name, data, channel, user.id, editor, delimiter)
    if api_id:
        se_command = generate_link_to_api(api_id, channel)
        trylink = """<a href="/{0}">{0}</a>""".format(api_id)
        out = "created {0} successfully <br><br> {1} <br><br>".format(trylink, se_command)
        return HTMLResponse(status_code=200,
                            content=CustomAPI.template.header(user) + out + CustomAPI.template.foot)
    else:
        return HTMLResponse(status_code=201, content=CustomAPI.template.header(user) + "Error making api" + CustomAPI.template.foot)


@router.get("/api/edit", response_class=HTMLResponse)
async def api_edit(id: int, user: CustomAPI.User = Depends(CustomAPI.security.is_loggedin_user)):
    owner = await backend.is_owner(user.id, id)
    editor = await backend.is_editor(user.id, id)

    if not owner:
        if not editor:
            return HTMLResponse(status_code=403, content=CustomAPI.template.header(user) + "Forbidden" + CustomAPI.template.foot)

    api = await backend.fetch_api(id)
    link = '<font size="+3">' + generate_link_to_api(api.id, api.channel) + "<br></font>"
    if editor:
        editor_id = user.id
    else:
        editor_id = 0
    # the default value in the form is space because the form will send a None if its truly empty.
    if api.channel == '':
        api.channel = ' '
    editform = await api_form("edit", "post", api.id, api.name, api.data, api.channel, editor_id, api.delimiter)
    editform = "<br>" + editform
    return HTMLResponse(status_code=200, content=CustomAPI.template.header(user) + link + editform + CustomAPI.template.foot)


@router.post("/api/edit", response_class=HTMLResponse)
async def api_edit(id: Annotated[int, Form()], name: Annotated[str, Form()],
                   data: Annotated[str, Form()], channel: Annotated[str, Form()],
                   editor: Annotated[int, Form()], delimiter: Annotated[str, Form()],
                   user: CustomAPI.User = Depends(CustomAPI.security.is_loggedin_user)):
    # if id and not data and not name and not channel:
    #    return RedirectResponse(url="/api/edit/{0}".format(id))
    if not await backend.is_owner(user.id, id) and not backend.is_editor(user.id, id):
        return HTMLResponse(status_code=403, content="Forbidden")
    # id: int,  name: str or None, data: str or None, channel: str or None,
    if channel == ' ':
        channel = ''
    if await backend.edit_api(id, name, data, channel, editor, delimiter):
        link = await generate_link_to_api(id, channel)
        ret = """<br> <a href="/api/edit?id={0}">edit</a>ed <a href="/{0}">{0}</a> successfully <br><br> {1} <br><br> """.format(id, link)
        return HTMLResponse(status_code=200, content=CustomAPI.template.header(user) + ret + CustomAPI.template.foot)
    else:
        return HTMLResponse(status_code=201, content=CustomAPI.template.header(user) + 'EDIT ERROR' + CustomAPI.template.foot)


@router.get("/api/delete", response_class=HTMLResponse)
async def api_delete(id: int, user: CustomAPI.User = Depends(CustomAPI.security.is_loggedin_user)):
    if not await backend.is_owner(user.id, id):
        return HTMLResponse(status_code=403, content="Forbidden")

    if await backend.delete_api(id):
        return HTMLResponse(status_code=200, content=CustomAPI.template.header(user) + "Deleted {0} successfully <br>".format(id) + CustomAPI.template.foot)
    else:
        return HTMLResponse(status_code=404, content=CustomAPI.template.header(user) + "Item not found" + CustomAPI.template.foot)


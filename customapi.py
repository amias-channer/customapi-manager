from fastapi import HTTPException, FastAPI, Depends, Header
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic

import CustomAPI
from Routers import user_router, api_router, api_form
from CustomAPI.template import head, foot, loginform
import random

app = FastAPI()
app.include_router(user_router)
app.include_router(api_router)

backend = CustomAPI.Backend()
security = HTTPBasic()


@app.get("/", response_class=HTMLResponse)
async def root():
    return head + loginform


@app.get("/start", response_class=HTMLResponse)
async def start(user: CustomAPI.User = Depends(CustomAPI.security.authenticate_user)):
    padding = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
    banner = """{0}<font size="+1">Welcome {1}</font><br><br>""".format(padding, user.name)
    apilist = """<form method="get">{0}<button type="submit" formaction="/api/delete">Delete</button>""".format(padding)
    optlist = """&nbsp;&nbsp;<select name='id'>"""
    for relation in backend.fetch_api_list(user.id):
        api = backend.fetch_api(relation.api_id)
        optlist += """<option value="{0}">{1}</option>""".format(api.id, api.name)
    optlist += "</select>"
    apilist += optlist
    apilist += """</select>&nbsp;&nbsp;<button type="submit" formaction="/api/edit">Edit</button></form>"""
    createform = api_form("create", "post", 0, "", "", "", 0)
    return CustomAPI.template.header(user) + apilist + createform + foot


@app.get("/shared", response_class=HTMLResponse)
async def shared(user: CustomAPI.Login = Depends(CustomAPI.security.authenticate_user)):
    padding = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
    banner = """{0}<font size="+1">Welcome {1}</font><br><br>""".format(padding, user.name)
    apilist = """<form method="get">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"""
    optlist = """<select name='id'>"""
    for relation in backend.fetch_shared_api_list(user.id):
        api = backend.fetch_api(relation.api_id)
        optlist += """<option value="{0}">{1}</option>""".format(api.id, api.name)
    optlist += "</select>"
    apilist += optlist
    apilist += """</select><button type="submit" formaction="/api/edit">Edit</button></form>"""
    return CustomAPI.template.header(user) + apilist + foot


@app.get("/{i}", response_class=HTMLResponse)
def shortcut(i: int, c: str or None = None, http_x_streamelements_channel: str | None = Header(default=None)):
    api = backend.fetch_api(i)
    import random
    out = random.choice(api.data.split(","))
    if api.channel:
        if http_x_streamelements_channel != api.channel:
            return HTMLResponse(status_code=403, content="Incorrect Channel in Header")
        if c:
            if api.channel != c:
                return HTMLResponse(status_code=403, content="Incorrect Channel")
    return HTMLResponse(status_code=200, content=out)


@app.get("/n/{n}", response_class=HTMLResponse)
def name(n: str, r: int or None = None):
    data = backend.fetch_api_by_name(n)
    if data:
        out = data.data
        if r == 1:
            out = random.choice(data.data.split(","))
        return HTMLResponse(status_code=200, content=out)
    else:
        return HTTPException(status_code=404, detail="Item not found")


@app.get("/r/{i}/{c}", response_model=None)
@app.get("/random/{i}/{c}", response_model=None)
def random(i: int, c: str, r: int = 1,
           user_agent: str | None = Header(default=None),
           http_x_streamelements_channel: str | None = Header(default=None)):
    return api(i, c, r, user_agent, http_x_streamelements_channel)


@app.get("/a/{i}/{c}", response_model=None)
@app.get("/api/{i}/{c}", response_model=None)
def api(i: int, c: str, r: int or None = None,
        user_agent: str | None = Header(default=None),
        http_x_streamelements_channel: str | None = Header(default=None)):
    # check headers
    allowed_user_agents = ['StreamElements Bot',
                           'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36']
    if user_agent not in allowed_user_agents:
        return HTMLResponse(status_code=403, content="Forbidden user agent")

    # if http_x_streamelements_channel != c:
    #    return HTMLResponse(status_code=403, content="Incorrect Headers")

    data = backend.fetch_api_data(i, c)
    if data:
        out = data
        if r == 1:
            bits = data.split(",")
            import random  # this import is here because some how random doesn't work without it
            out = random.choice(bits)
        return HTMLResponse(status_code=200, content=out)
    else:
        return HTTPException(status_code=404, detail="Item not found")


from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import api
import fixtures  # beware import order matters!

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(api.router)
templates = Jinja2Templates(directory="static/templates")


@app.get("/product/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):

    return templates.TemplateResponse("item.html", {"request": request, "id": id, "random_var": "some stuff"})


@app.on_event("startup")
def on_startup():
    fixtures.create_db()
    fixtures.create_data()


@app.get("/")
async def root():
    return {"message": "Hello World"}




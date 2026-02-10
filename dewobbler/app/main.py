from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

from app.api.v1 import processes
from app.api.v1 import debugger
from app.core.config import settings

templates = Jinja2Templates(directory="app/templates")

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"/api/v1/openapi.json"
    )

    app.include_router(processes.router, prefix="/api/v1")
    app.include_router(debugger.router, prefux="/api/v1")

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    return app

app = create_application()
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

import logging
import uvicorn

from app.helpers.get_processes import get_python_processes

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)
logger.debug("Test DEBUG msg")

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/processes", response_class=HTMLResponse)
async def all_processes(request: Request):
    python_processes = get_python_processes()
    print(f"DEBUG: {python_processes}", flush=True)
    return templates.TemplateResponse("processes_fragment.html", {"request": request, "python_processes": python_processes})
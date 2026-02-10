from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

import logging

from app.helpers.get_processes import get_python_processes

logger = logging.getLogger("uvicorn")

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/processes", response_class=HTMLResponse)
async def all_processes(request: Request):
    """Returns the table of running processes as HTMX fragment."""
    python_processes = get_python_processes()
    return templates.TemplateResponse(
        "processes_fragment.html", {
            "request": request, 
            "python_processes": python_processes
        })

@router.get("/attach/{pid}", response_class=HTMLResponse)
async def attach_console(request: Request, pid: int):
    """Servers the full-page console UI."""
    return templates.TemplateResponse(
        "console.html", {
            "request": request,
            "pid": pid
        })
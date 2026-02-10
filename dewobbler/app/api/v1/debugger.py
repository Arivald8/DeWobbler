from app.services.injector import ProcessInjector
from app.services.debug_manager import get_session
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import logging
import json

router = APIRouter()
logger = logging.getLogger("uvicorn")

@router.websocket("/ws/attach/{pid}")
async def websocket_debugger(websocket: WebSocket, pid: int):
    await websocket.accept()

    session = get_session(pid)
    session.browser_ws = websocket

    injector = ProcessInjector(pid)
    success = await injector.attach()

    if not success:
        # Send error as OOB HTML so it appears in the terminal
        err = '<div id="terminal-output" hx-swap-oob="beforeend" class="text-red-500">Error: Failed to inject debugger script.</div>'
        await websocket.send_text(err)
        await websocket.close()
        return
    
    # Send a waiting message
    msg = '<div id="terminal-output" hx-swap-oob="beforeend" class="text-gray-500">Waiting for PID connection...</div>'
    await websocket.send_text(msg)

    try:
        # Wait for the process to phone home (5s timeout)
        try:
            await asyncio.wait_for(session.connected_event.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            err = '<div id="terminal-output" hx-swap-oob="beforeend" class="text-red-500">Error: Timed out waiting for process response.</div>'
            await websocket.send_text(err)

        while True:
            raw_data = await websocket.receive_text()
            try:
                payload = json.loads(raw_data)
                command = payload.get("command", "")
                await session.send_command(command)
            except json.JSONDecodeError:
                # fallback if raw text is sent
                await session.send_command(raw_data)

    except WebSocketDisconnect:
        logger.info(f"Browser disconnected from session {pid}")
        session.browser_ws = None
    except Exception as e:
        logger.error(f"WS Error: {e}")
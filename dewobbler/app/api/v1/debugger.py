from app.services.injector import ProcessInjector
from app.services.debug_manager import get_session
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import logging

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
        await websocket.send_text("Error: Failed to inject debugger script.\n")
        await websocket.close()
        return
    
    await websocket.send_text(f"Waiting for PID {pid} to connect back...\n")

    try:
        # Wait for the process to phone home (5s timeout)
        try:
            await asyncio.wait_for(session.connected_event.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            await websocket.send_text("Error: Times out waiting for process response.\n")
            
        while True:
            data = await websocket.receive_text() # from browser
            # Forwarded to target process via TCP bridge
            await session.send_command(data)

    except WebSocketDisconnect:
        logger.info(f"Browser disconnected from session {pid}")
        session.browser_ws = None
    except Exception as e:
        logger.error(f"WS Error: {e}")
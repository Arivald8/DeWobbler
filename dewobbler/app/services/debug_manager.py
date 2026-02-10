

import html
import asyncio
import logging
from typing import Dict, Optional

logger = logging.getLogger("uvicorn")

class DebugSession:
    """
    Manages the lifecycle of a single debug session.
    Acts as bridge between the browser WebSocket and
    the target process TCP connection.
    """
    def __init__(self, pid: int):
        self.pid = pid
        self.browser_ws = None # Will be set when browser connects
        self.process_reader: Optional[asyncio.StreamReader] = None
        self.process_writer: Optional[asyncio.StreamWriter] = None
        self.server: Optional[asyncio.Server] = None
        self.port: int = 0
        self.connected_event = asyncio.Event()

    async def start_server(self):
        """Start a one-time TCP server waiting for target process to call home."""
        self.server = await asyncio.start_server(
            self.handle_process_connection, "127.0.0.1", 0
        )
        addr = self.server.sockets[0].getsockname()
        self.port = addr[1]
        logger.info(f"Debug server for PID {self.pid}. Port: {self.port}")

    async def stop(self):
        if self.process_writer:
            self.process_writer.close()
        if self.server:
            self.server.close()
            await self.server.wait_closed()

    async def handle_process_connection(self, reader, writer):
        """Called when the target process connects back."""
        if self.process_writer:
            logger.warning(f"Duplicate connection attempt for PID {self.pid}")
            writer.close()
            return
        
        logger.info(f"Target PID {self.pid} connected successfully.")
        self.process_reader = reader
        self.process_writer = writer
        self.connected_event.set()

        # Background loop to pump stdout from process -> browser
        asyncio.create_task(self.pump_output())

    async def pump_output(self):
        """Reads stdout/stderr from the process and sends it to the browser."""
        try:
            while True:
                data = await self.process_reader.read(4096)
                if not data:
                    break

                if self.browser_ws:
                    text_data = data.decode("utf-8", errors="replace")
                    safe_text = html.escape(text_data)

                    # Wrapping in an out of band swap for htmx
                    # taget="#terminal-output" tells htmx where to put it.
                    # hx-swap-oob="beforeend" tells it to append.
                    message = f'<div id="terminal-output" hx-swap-oob="beforeend">{safe_text}</div>'
                    await self.browser_ws.send_text(message)
                    
        except Exception as e:
            logger.error(f"Error pumping output for PID {self.pid}: {e}")
        finally:
            logger.info(f"Connection from PID {self.pid} closed.")

    async def send_command(self, cmd: str):
        """Sends python cmd from the browser to the target process."""
        if not self.process_writer:
            if self.browser_ws:
                await self.browser_ws.send_text(">> Error: Target not connected yet.\n")
            return
        
        # Write cmd + newline so the REPL loop processes it
        self.process_writer.write(f"{cmd}\n".encode("utf-8"))
        await self.process_writer.drain()

# Global singleton to hold active sessions. Maybe Redis in the future
active_sessions: Dict[int, DebugSession] = {}

def get_session(pid: int) -> DebugSession:
    if pid not in active_sessions:
        active_sessions[pid] = DebugSession(pid)
    return active_sessions[pid]
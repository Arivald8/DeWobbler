import asyncio
import logging
import socket
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

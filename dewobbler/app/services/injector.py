import logging
from app.services.debug_manager import get_session
from app.services.bootstrap_code import get_bootstrap_code

logger = logging.getLogger("uvicorn")

class ProcessInjector:
    def __init__(self, pid: int):
        self.pid = pid

    async def attach(self) -> bool:
        """Prepares the session and performs the injection."""
        session = get_session(self.pid)

        if not session.server:
            await session.start_server()

        bootstrap_code = get_bootstrap_code(session.port)
        
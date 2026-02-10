import os
import sys
import tempfile
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
        
        # Writing to a temp file as sys.remote_exec requires a file path
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
                tmp.write(bootstrap_code)
                tmp_path = tmp.name

            if hasattr(sys, "remote_exec"):
                logger.info(f"Injecting into PID {self.pid} via sys.remote_exec")
                sys.remote_exec(self.pid, tmp_path)
            else:
                logger.warning("sys.remote_exec missing. Simulate mode.")
                import threading
                def sim():
                    # Helper to simulate the callback for testing without 3.14.3
                    os.system(f"{sys.executable} {tmp_path}")
                threading.Thread(target=sim).start()

            return True
        
        except Exception as e:
            logger.error(f"Injection failed: {e}")
            return False
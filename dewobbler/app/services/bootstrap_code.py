def get_bootstrap_code(session_port):
    """
    This script runs INSIDE the target process.
    It connects back to FastAPI server and starts a read/exec loop.
    """
    return """
import sys
import socket
import threading
import code
import contextlib

def _remote_debug_client(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        
        # file-like object for the socket
        f = s.makefile('rw', buffering=1, encoding='utf-8')
        
        # need to hook stdout/stderr to this socket.
        # simple REPL loop
        
        def run_repl():
            # Redirect standard streams to the socket
            with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                print(f"\\n Attached to PID {{os.getpid()}}")
                print("Standard Output Redirected")
                
                console = code.InteractiveConsole(locals=locals())
                
                # reading lines manually from the socket to feed the console
                while True:
                    try:
                        line = f.readline()
                        if not line: break
                        # removing trailing newline for push
                        console.push(line.rstrip('\\n'))
                    except Exception as ex:
                        print(f"REPL Error: {{ex}}")
                        break
            
            s.close()

        # Running in a separate thread to avoid blocking the main loop indefinitely
        # (Though sys.remote_exec runs on the main thread, we spawn a thread 
        # to keep the connection alive while the main thread continues its work)
        t = threading.Thread(target=run_repl, daemon=True)
        t.start()
        
    except Exception as e:
        # If we can't connect, we can't report it easily.
        pass

# Exec
import os
_remote_debug_client('127.0.0.1', {session_port})
"""
def get_bootstrap_code(session_port):
    """
    This script runs INSIDE the target process.
    It connects back to FastAPI server and starts a read/exec loop.
    """
    return f"""
import sys
import socket
import threading
import code
import contextlib
import time

def _remote_debug_client(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        
        f = s.makefile('rw', buffering=1, encoding='utf-8')
    
        def run_repl():
            with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                print(f"\\n Attached to PID {{os.getpid()}}")

                target_locals = locals() # fallback
                try:
                    main_thread = threading.main_thread()
                    
                    # Getting current stack frame of the main thread
                    frames = sys._current_frames()
                    frame = frames.get(main_thread.ident)

                    # Walking up the stack if stuck in a sys call like time.sleep
                    while frame:
                        # If in sleep or an import, go up
                        # or check if var we want exists (just for this specific one)
                        # grab the frame below the top if inside a library call
                        if frame.f_code.co_filename.endswith("tester.py"):
                            target_locals = frame.f_locals
                            print(f"Context switched to Main Thread (Frame: {{frame.f_code.co_name}})")
                            break
                        frame = frame.f_back

                except Exception as e:
                    print(f"Warning: Could not bind to main thread: {{e}}")
                
                console = code.InteractiveConsole(locals=target_locals)
                
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
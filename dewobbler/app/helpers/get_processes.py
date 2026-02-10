import psutil

def get_python_processes():
    processes = []
    for proc in psutil.process_iter(["pid", "name", "exe", "cmdline", "username"]):
        try:
            info = proc.info
            name = info.get("name") or ""
            cmdline = info.get("cmdline") or []
            exe = info.get("exe") or ""
            username = info.get("username") or ""

            if name.lower().startswith(("python", "pythonw")) \
               or "python" in exe.lower() \
               or (cmdline and "python" in cmdline[0].lower()):
                processes.append({
                    "pid": info["pid"],
                    "name": name,
                    "username": username,
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes

import time
import os

def main():
    print(f"Tester process started. PID: {os.getpid()}")
    print("Waiting for debugger attachment...")

    counter = 0
    while True:
        # Printing to stdout to prove debugger can capture it later
        # though remote_exec captures its own injected stdout,
        # not the process's native loop output unless sys.stdout is
        # hooked globally.
        time.sleep(2)
        counter += 1

        # A var to inspect from the debugger
        secret_status = f"Running for {counter * 2} seconds"

if __name__ == "__main__":
    main()

        
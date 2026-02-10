import time
import os

def main():
    print(f"Tester process started. PID: {os.getpid()}")
    print("Waiting for debugger attachment...")

    counter = 0
    while True:
        time.sleep(2)
        counter += 1
        secret_status = f"Running for {counter * 2} seconds"

if __name__ == "__main__":
    main()

        
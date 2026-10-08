import os
import subprocess
import time
import urllib.request
import webbrowser
import sys

def check_cmd(cmd, name):
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
        return True
    except Exception:
        print(f"{name} is not installed or not available in PATH.")
        return False

def main():
    print("Checking environment...")
    if not check_cmd("python --version", "Python"): sys.exit(1)
    if not check_cmd("node --version", "Node.js"): sys.exit(1)
    if not check_cmd("npm --version", "npm"): sys.exit(1)

    print("Environment checks passed.")

    # Check if backend is already running
    try:
        urllib.request.urlopen("http://127.0.0.1:8000/docs", timeout=2)
        print("SAHYAT IS ALREADY RUNNING")
        
        # Find the active frontend port
        ready_port = None
        for port in range(5173, 5180):
            try:
                urllib.request.urlopen(f"http://localhost:{port}", timeout=0.5)
                ready_port = port
                break
            except Exception:
                pass
        
        if ready_port:
            webbrowser.open(f"http://localhost:{ready_port}")
        else:
            print("Backend is running, but couldn't verify frontend port. Opening default.")
            webbrowser.open("http://localhost:5173")
        sys.exit(0)
    except Exception:
        pass

    print("Starting backend...")
    # Use CREATE_NEW_CONSOLE to open in a new window
    backend_cmd = "title Sahyat Backend & python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"
    CREATE_NEW_CONSOLE = 0x00000010
    backend_proc = subprocess.Popen(f'cmd /c "{backend_cmd}"', creationflags=CREATE_NEW_CONSOLE)

    print("Waiting for backend to become ready...")
    ready = False
    for i in range(30):
        try:
            urllib.request.urlopen("http://127.0.0.1:8000/docs", timeout=1)
            ready = True
            break
        except Exception:
            time.sleep(1)

    if not ready:
        print("SAHYAT BACKEND FAILED TO START")
        print("Please check the 'Sahyat Backend' window for errors.")
        sys.exit(1)

    print("Backend is ready!")

    if not os.path.exists(os.path.join("frontend", "node_modules")):
        print("Installing frontend dependencies...")
        subprocess.run("npm install", cwd="frontend", shell=True)

    print("Starting frontend...")
    frontend_cmd = "title Sahyat Frontend & npm run dev"
    frontend_proc = subprocess.Popen(f'cmd /c "{frontend_cmd}"', cwd="frontend", creationflags=CREATE_NEW_CONSOLE)

    print("Waiting for frontend to become ready...")
    ready_port = None
    for i in range(30):
        for port in range(5173, 5180):
            try:
                urllib.request.urlopen(f"http://localhost:{port}", timeout=0.5)
                ready_port = port
                break
            except Exception:
                pass
        if ready_port:
            break
        time.sleep(1)

    if not ready_port:
        print("SAHYAT FRONTEND FAILED TO START")
        print("Please check the 'Sahyat Frontend' window for errors.")
        sys.exit(1)

    print(f"Frontend is ready on port {ready_port}!")
    print("Opening browser...")
    webbrowser.open(f"http://localhost:{ready_port}")

if __name__ == "__main__":
    main()

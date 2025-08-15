import subprocess
import webbrowser
import time

# Start the Flask server in a subprocess
server = subprocess.Popen(["python", "server.py"])

# Wait a moment for the server to start
time.sleep(2)

# Open the frontend in the default browser
webbrowser.open("http://localhost:5000")

# Wait for the server process to finish (optional)
try:
    server.wait()
except KeyboardInterrupt:
    server.terminate()

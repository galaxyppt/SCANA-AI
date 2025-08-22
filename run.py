"""Run script for SCANA-AI application."""

import subprocess
import sys
import os
import signal
import time
from threading import Thread, Event
import uvicorn
import socket
from contextlib import closing

def find_free_port(start_port: int, max_attempts: int = 10) -> int:
    """Find a free port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            try:
                sock.bind(('127.0.0.1', port))
                sock.listen(1)
                return port
            except socket.error:
                continue
    raise RuntimeError(f"Could not find a free port in range {start_port}-{start_port + max_attempts}")

# Event to signal when to stop the API server
stop_event = Event()

def run_api(port: int):
    """Run the FastAPI server."""
    try:
        uvicorn.run("src.api.routes:app", host="127.0.0.1", port=port)
    except Exception as e:
        print(f"Error running API server: {str(e)}")

def run_streamlit(api_port: int):
    """Run the Streamlit app."""
    try:
        # Get the absolute path to the app.py file
        app_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "src", "ui", "app.py"
        )
        
        # Set environment variable for API port
        os.environ["SCANA_API_PORT"] = str(api_port)
        
        # Find a free port for Streamlit
        streamlit_port = find_free_port(8501)
        
        subprocess.run([
            sys.executable,
            "-m", "streamlit",
            "run", app_path,
            "--server.port", str(streamlit_port)
        ])
    except Exception as e:
        print(f"Error running Streamlit app: {str(e)}")

def cleanup(signum, frame):
    """Clean up resources before exiting."""
    print("\nShutting down servers...")
    stop_event.set()
    
    # Clean up any temporary files
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
    if os.path.exists(temp_dir):
        try:
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                try:
                    os.unlink(file_path)
                except Exception as e:
                    print(f"Error removing file {file_path}: {str(e)}")
        except Exception as e:
            print(f"Error cleaning up temp directory: {str(e)}")
    
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers for cleanup
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # Create temp directory if it doesn't exist
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Find available ports
        api_port = find_free_port(8088)
        
        print("Starting SCANA-AI servers...")
        print(f"API server will run at: http://127.0.0.1:{api_port}")
        print("Streamlit app will run at: http://127.0.0.1:8501")
        
        # Start API server in a separate thread
        api_thread = Thread(target=run_api, args=(api_port,), daemon=True)
        api_thread.start()
        
        # Wait a moment for the API server to start
        time.sleep(2)
        
        # Run Streamlit app in main thread
        run_streamlit(api_port)
    except Exception as e:
        print(f"Error starting servers: {str(e)}")
        sys.exit(1) 
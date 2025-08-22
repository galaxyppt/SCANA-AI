"""Run script for SCANA-AI API server."""

import uvicorn
from src.api.routes import app

if __name__ == "__main__":
    print("Starting API server...")
    uvicorn.run(app, host="127.0.0.1", port=8001) 
"""Demo runner script for SCANA-AI."""

import subprocess
import sys
import os
import signal
import time
from threading import Thread, Event
import uvicorn
from src.api.routes import app as api_app
from src.core.persistence.data_store import DataStore
from src.core.services.analysis_service import AnalysisService
from src.core.services.monitoring_service import MonitoringService
import pandas as pd

# Event to signal when to stop the API server
stop_event = Event()

def setup_demo_data():
    """Set up demo data for testing."""
    try:
        # Initialize services
        data_store = DataStore()
        analysis_service = AnalysisService()
        monitoring_service = MonitoringService(data_store)
        
        # Process demo contract
        contract_file = os.path.join("data", "demo_vendor1.pdf")
        if os.path.exists(contract_file):
            analysis = analysis_service.analyze_contract(contract_file)
            if 'error' not in analysis:
                data_store.save_analysis("demo_vendor1", analysis)
                print("✅ Demo contract processed successfully")
            else:
                print("❌ Error processing demo contract:", analysis['error'])
        
        # Load demo delivery data
        delivery_file = os.path.join("data", "demo_delivery.csv")
        if os.path.exists(delivery_file):
            delivery_data = pd.read_csv(delivery_file)
            monitoring_service.update_delivery_data(delivery_data)
            print("✅ Demo delivery data loaded successfully")
        
        return True
    except Exception as e:
        print("❌ Error setting up demo data:", str(e))
        return False

def run_api():
    """Run the FastAPI server."""
    try:
        uvicorn.run(api_app, host="127.0.0.1", port=8000)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"❌ Error running API server: {str(e)}")

def run_streamlit():
    """Run the Streamlit app."""
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "src/ui/app.py"])
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"❌ Error running Streamlit app: {str(e)}")

def cleanup(signum, frame):
    """Clean up resources before exiting."""
    print("\n🔄 Shutting down servers...")
    stop_event.set()
    
    # Clean up any temporary files
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
    if os.path.exists(temp_dir):
        try:
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"⚠️ Error removing file {file_path}: {str(e)}")
        except Exception as e:
            print(f"⚠️ Error cleaning up temp directory: {str(e)}")
    
    sys.exit(0)

if __name__ == "__main__":
    print("\n🚀 Starting SCANA-AI Demo...")
    
    # Register signal handlers for cleanup
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # Create temp directory if it doesn't exist
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Set up demo data
    if not setup_demo_data():
        print("❌ Failed to set up demo data. Exiting...")
        sys.exit(1)
    
    print("\n🌐 Starting servers...")
    print("📡 API server will run at: http://127.0.0.1:8000")
    print("🖥️ Streamlit app will run at: http://127.0.0.1:8501")
    
    # Start API server in a separate thread
    api_thread = Thread(target=run_api, daemon=True)
    api_thread.start()
    
    # Wait a moment for the API server to start
    time.sleep(2)
    print("\n✨ API server started successfully")
    
    # Run Streamlit app in main thread
    print("🚀 Starting Streamlit app...")
    run_streamlit() 
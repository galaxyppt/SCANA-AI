"""Data persistence layer for SCANA-AI."""

import json
import os
import tempfile
from typing import Dict, Any, List
from datetime import datetime

class DataStore:
    """Handles data persistence for the application."""
    
    def __init__(self):
        """Initialize the data store."""
        self.temp_dir = tempfile.gettempdir()
        self.data_file = os.path.join(self.temp_dir, "scana_delivery_data.json")
    
    def save_delivery_data(self, data: Dict[str, Any]) -> bool:
        """Save delivery data to file."""
        try:
            # Write the data with proper encoding
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                # Ensure the file is written to disk
                f.flush()
                os.fsync(f.fileno())
            return True
        except Exception as e:
            print(f"Error saving delivery data: {str(e)}")
            # Try alternative location if primary fails
            try:
                alt_file = os.path.join(os.getcwd(), "delivery_data.json")
                with open(alt_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
                print(f"Data saved to alternative location: {alt_file}")
                return True
            except Exception as e2:
                print(f"Error saving to alternative location: {str(e2)}")
                return False
    
    def load_delivery_data(self) -> List[Dict[str, Any]]:
        """Load delivery data from file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return [data]
                    return data
            return []
        except Exception as e:
            print(f"Error loading delivery data: {str(e)}")
            return []
    
    def append_delivery_data(self, new_data: Dict[str, Any]) -> bool:
        """Append new delivery data to existing records."""
        try:
            existing_data = self.load_delivery_data()
            existing_data.append(new_data)
            return self.save_delivery_data(existing_data)
        except Exception as e:
            print(f"Error appending delivery data: {str(e)}")
            return False 
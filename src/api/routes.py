"""SCANA-AI API routes for delivery monitoring."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict
import random

from ..core.persistence.data_store import DataStore
from ..core.services.analysis_service import AnalysisService

app = FastAPI(
    title="SCANA-AI API",
    description="Smart Contract Analysis & Network Automation API",
    version="1.0.0"
)

# Initialize services
data_store = DataStore()
analysis_service = AnalysisService()

# Sample vendor data
VENDORS = [
    "Fresh Foods Inc.",
    "Quick Delivery LLC",
    "Cool Transport Co.",
    "Speedy Logistics",
    "Express Cargo Ltd."
]

class DeliveryData(BaseModel):
    """Delivery data model."""
    vendor_name: str
    delivery_date: str
    delivery_time: str
    delivery_temperature: float
    product_quality_score: float
    industry: Optional[str] = "Food"
    product_type: Optional[str] = "refrigerated"

def generate_random_delivery():
    """Generate random delivery data for testing."""
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_hour = datetime.now().hour
    
    return {
        "vendor_name": random.choice(VENDORS),
        "delivery_date": current_date,
        "delivery_time": f"{str(current_hour).zfill(2)}:{str(random.randint(0, 59)).zfill(2)}",
        "delivery_temperature": round(random.uniform(2.0, 8.0), 1),
        "product_quality_score": round(random.uniform(80, 100), 1)
    }

@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "status": "ok",
        "message": "SCANA-AI Delivery Monitoring API",
        "data_file": data_store.data_file
    }

@app.get("/deliveries")
def get_deliveries():
    """Get latest delivery data."""
    try:
        delivery = generate_random_delivery()
        if data_store.save_delivery_data(delivery):
            return {
                "status": "success",
                "data": delivery,
                "file_location": data_store.data_file
            }
        raise HTTPException(status_code=500, detail="Failed to save delivery data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/deliveries/batch")
def get_delivery_batch(count: int = 10):
    """Get a batch of delivery data."""
    try:
        deliveries = [generate_random_delivery() for _ in range(count)]
        if data_store.save_delivery_data(deliveries):
            return {
                "status": "success",
                "data": deliveries,
                "file_location": data_store.data_file
            }
        raise HTTPException(status_code=500, detail="Failed to save delivery data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/deliveries")
def create_delivery(delivery: DeliveryData):
    """Create a new delivery record."""
    try:
        delivery_dict = delivery.dict()
        if data_store.append_delivery_data(delivery_dict):
            return {
                "status": "success",
                "data": delivery_dict,
                "file_location": data_store.data_file
            }
        raise HTTPException(status_code=500, detail="Failed to save delivery data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
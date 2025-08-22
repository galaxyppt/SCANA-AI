from fastapi import FastAPI, HTTPException
from datetime import datetime
import random
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="SCANA-AI Live Delivery API",
    description="Real-time delivery data simulation for SLA tracking",
    version="1.0.0"
)

# Sample vendors for simulation
VENDORS = [
    "Fresh Foods Inc.",
    "Quick Delivery LLC",
    "Cool Transport Co.",
    "Speedy Logistics",
    "Express Cargo Ltd."
]

class DeliveryData(BaseModel):
    """Pydantic model for delivery data."""
    vendor_name: str
    delivery_date: str
    delivery_time: str
    delivery_temperature: float
    product_quality_score: int

def generate_delivery_data() -> DeliveryData:
    """Generate random delivery data."""
    now = datetime.now()
    return DeliveryData(
        vendor_name=random.choice(VENDORS),
        delivery_date=now.strftime("%Y-%m-%d"),
        delivery_time=now.strftime("%H:%M:%S"),
        delivery_temperature=round(random.uniform(0, 12), 1),
        product_quality_score=random.randint(70, 100)
    )

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "SCANA-AI Live Delivery API",
        "status": "running",
        "endpoints": [
            "/deliveries",
            "/deliveries/batch"
        ]
    }

@app.get("/deliveries", response_model=DeliveryData)
async def get_delivery():
    """Get a single simulated delivery data point."""
    try:
        return generate_delivery_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/deliveries/batch", response_model=List[DeliveryData])
async def get_delivery_batch(count: int = 5):
    """Get multiple simulated delivery data points."""
    try:
        if count < 1 or count > 50:
            raise HTTPException(
                status_code=400,
                detail="Count must be between 1 and 50"
            )
        return [generate_delivery_data() for _ in range(count)]
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
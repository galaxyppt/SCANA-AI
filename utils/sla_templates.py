"""SLA templates for different industries."""

from typing import Dict, Any

def get_indian_food_sla() -> Dict[str, Any]:
    """Indian food industry SLA template."""
    return {
        "delivery_time": {
            "standard_delivery": "Within 24 hours of order placement",
            "perishable_items": "Within 12 hours of order placement",
            "emergency_orders": "Within 6 hours of order placement"
        },
        "cold_chain_requirement": {
            "dairy_products": "2°C to 8°C",
            "frozen_foods": "-18°C or below",
            "prepared_meals": "Below 5°C",
            "monitoring": "Continuous temperature logging required"
        },
        "hygiene_standards": {
            "fssai_compliance": "Mandatory FSSAI certification",
            "staff_requirements": "Food handling certification required",
            "facility_standards": "ISO 22000 certification",
            "cleaning_protocol": "Daily sanitation records"
        },
        "penalties": {
            "temperature_violation": "₹10,000 per incident",
            "delivery_delay": "5% of order value per hour",
            "hygiene_violation": "₹50,000 and possible contract termination"
        }
    }

def get_global_cold_chain_sla() -> Dict[str, Any]:
    """Global cold chain and pharma SLA template."""
    return {
        "delivery_time": {
            "standard_delivery": "Within 48 hours internationally",
            "temperature_sensitive": "Express delivery within 24 hours",
            "critical_supplies": "Within 12 hours with tracking"
        },
        "cold_chain_requirement": {
            "vaccines": "2°C to 8°C",
            "biologics": "-20°C to -10°C",
            "ultra_cold": "-80°C to -60°C",
            "monitoring": "GPS and temperature logging mandatory"
        },
        "hygiene_standards": {
            "gmp_compliance": "WHO GMP certification required",
            "clean_room": "ISO Class 7 or better",
            "staff_training": "GDP certification mandatory",
            "contamination_control": "Regular sterility testing"
        },
        "penalties": {
            "temperature_excursion": "$5000 per incident",
            "delivery_delay": "10% of shipment value per day",
            "documentation_error": "$1000 per incident"
        }
    }

def get_bfsi_sla() -> Dict[str, Any]:
    """Banking, Financial Services and Insurance SLA template."""
    return {
        "delivery_time": {
            "document_processing": "Within 4 business hours",
            "urgent_requests": "Within 2 business hours",
            "standard_requests": "Within 1 business day"
        },
        "security_requirements": {
            "data_encryption": "AES-256 encryption mandatory",
            "access_control": "Multi-factor authentication",
            "audit_trail": "Complete activity logging"
        },
        "service_standards": {
            "accuracy": "99.99% accuracy in processing",
            "system_uptime": "99.95% availability",
            "response_time": "< 3 seconds for online transactions"
        },
        "penalties": {
            "security_breach": "Up to ₹1 crore per incident",
            "service_downtime": "₹10,000 per hour",
            "data_loss": "Contract termination and damages"
        }
    }

def get_sla_template(industry: str) -> Dict[str, Any]:
    """Get SLA template based on industry."""
    templates = {
        "Food": get_indian_food_sla(),
        "Pharma": get_global_cold_chain_sla(),
        "BFSI": get_bfsi_sla()
    }
    return templates.get(industry, get_indian_food_sla()) 
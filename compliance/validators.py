"""Validation functions for SLA compliance."""

from typing import Dict, Tuple, List
from datetime import datetime
import re

def validate_temperature(data: Dict[str, float], industry: str) -> Tuple[bool, str, float]:
    """
    Validate temperature data against industry standards.
    
    Args:
        data: Dictionary containing temperature readings
        industry: Industry type for specific thresholds
        
    Returns:
        Tuple of (is_valid, message, violation_severity)
    """
    temp = data.get('delivery_temperature', 0.0)
    
    thresholds = {
        "Food": {
            "dairy": (2.0, 8.0),
            "frozen": (-18.0, -12.0),
            "ambient": (15.0, 25.0)
        },
        "Pharma": {
            "refrigerated": (2.0, 8.0),
            "frozen": (-20.0, -10.0),
            "ultra_cold": (-80.0, -60.0)
        }
    }
    
    industry_rules = thresholds.get(industry, thresholds["Food"])
    product_type = data.get('product_type', 'refrigerated')
    
    if product_type in industry_rules:
        min_temp, max_temp = industry_rules[product_type]
        if min_temp <= temp <= max_temp:
            return True, "Temperature within acceptable range", 0.0
        
        violation_severity = min(
            abs(temp - min_temp) / min_temp,
            abs(temp - max_temp) / max_temp
        ) * 100
        
        return False, f"Temperature {temp}°C outside range ({min_temp}°C to {max_temp}°C)", violation_severity
    
    return False, "Unknown product type", 100.0

def validate_hygiene(data: Dict[str, str], industry: str) -> Tuple[bool, List[str]]:
    """
    Validate hygiene standards compliance.
    
    Args:
        data: Dictionary containing hygiene-related data
        industry: Industry type for specific standards
        
    Returns:
        Tuple of (is_compliant, list_of_violations)
    """
    violations = []
    
    standards = {
        "Food": {
            "certifications": ["FSSAI", "ISO22000"],
            "staff_requirements": ["food_handler_cert"],
            "facility_checks": ["daily_sanitation", "pest_control"]
        },
        "Pharma": {
            "certifications": ["WHO_GMP", "ISO9001"],
            "staff_requirements": ["gdp_cert"],
            "facility_checks": ["sterility_test", "contamination_control"]
        }
    }
    
    industry_standards = standards.get(industry, standards["Food"])
    
    # Check certifications
    certs = data.get('certifications', [])
    missing_certs = [cert for cert in industry_standards['certifications'] 
                    if cert not in certs]
    if missing_certs:
        violations.append(f"Missing certifications: {', '.join(missing_certs)}")
    
    # Check staff requirements
    staff_reqs = data.get('staff_requirements', [])
    missing_reqs = [req for req in industry_standards['staff_requirements'] 
                   if req not in staff_reqs]
    if missing_reqs:
        violations.append(f"Missing staff requirements: {', '.join(missing_reqs)}")
    
    # Check facility requirements
    facility_checks = data.get('facility_checks', [])
    missing_checks = [check for check in industry_standards['facility_checks'] 
                     if check not in facility_checks]
    if missing_checks:
        violations.append(f"Missing facility checks: {', '.join(missing_checks)}")
    
    return len(violations) == 0, violations

def validate_delivery_time(data: Dict[str, str], sla_requirements: Dict[str, str]) -> Tuple[bool, str, float]:
    """
    Validate delivery time against SLA requirements.
    
    Args:
        data: Dictionary containing delivery timing data
        sla_requirements: Dictionary containing SLA time requirements
        
    Returns:
        Tuple of (is_on_time, message, delay_in_hours)
    """
    try:
        delivery_time = datetime.strptime(
            f"{data['delivery_date']} {data['delivery_time']}", 
            "%Y-%m-%d %H:%M"
        )
        scheduled_time = datetime.strptime(
            f"{data['scheduled_date']} {data['scheduled_time']}", 
            "%Y-%m-%d %H:%M"
        )
        
        delay = (delivery_time - scheduled_time).total_seconds() / 3600  # hours
        
        if delay <= 0:
            return True, "Delivery on time", 0.0
        
        # Get allowed delay from SLA
        allowed_delay = 24  # default 24 hours
        if 'standard_delivery' in sla_requirements:
            # Extract hours from SLA text (e.g., "Within 24 hours")
            match = re.search(r'(\d+)\s*hours?', sla_requirements['standard_delivery'])
            if match:
                allowed_delay = float(match.group(1))
        
        if delay <= allowed_delay:
            return True, f"Delivery within SLA ({delay:.1f} hours)", delay
        
        return False, f"Delivery delayed by {delay:.1f} hours", delay
        
    except (KeyError, ValueError) as e:
        return False, f"Error validating delivery time: {str(e)}", 0.0 
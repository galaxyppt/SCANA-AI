"""Configuration settings for SCANA-AI."""

# Food Safety Standards
TEMPERATURE_RANGES = {
    'frozen': {'min': -23.0, 'max': -18.0, 'warning_buffer': 2.0},
    'cold_chain': {'min': 2.0, 'max': 8.0, 'warning_buffer': 1.0},
    'ambient': {'min': 10.0, 'max': 25.0, 'warning_buffer': 2.0},
}

# Quality Thresholds
QUALITY_THRESHOLDS = {
    'critical': 90,  # Essential food safety items
    'major': 85,     # Important quality standards
    'minor': 80,     # Minor quality issues
}

# Time Windows (in minutes)
DELIVERY_WINDOWS = {
    'early_morning': {'start': '04:00', 'end': '07:00'},
    'breakfast': {'start': '07:00', 'end': '09:00'},
    'lunch': {'start': '11:00', 'end': '13:00'},
    'dinner': {'start': '17:00', 'end': '20:00'},
}

# Vendor Categories
VENDOR_CATEGORIES = {
    'dairy_suppliers': ['dairy', 'milk', 'curd', 'paneer'],
    'quick_service': ['qsr', 'fast food', 'quick service'],
    'cold_chain': ['frozen', 'cold storage', 'ice cream'],
    'fresh_produce': ['vegetables', 'fruits', 'produce'],
    'bakery': ['bakery', 'bread', 'pastry'],
    'meat_poultry': ['meat', 'chicken', 'fish', 'seafood'],
}

# Regional Requirements
REGIONAL_REQUIREMENTS = {
    'north_india': {
        'summer': {
            'min': 0.0,
            'max': 6.0,
            'warning_buffer': 1.5
        }
    },
    'south_india': {
        'summer': {
            'min': 1.0,
            'max': 7.0,
            'warning_buffer': 1.5
        }
    },
    'coastal': {
        'summer': {
            'min': 2.0,
            'max': 8.0,
            'warning_buffer': 2.0
        }
    }
}

# Food Safety Standards
FOOD_SAFETY_STANDARDS = {
    'temperature_control': {
        'critical_limits': TEMPERATURE_RANGES,
        'monitoring_frequency': 'continuous',
        'corrective_action': 'immediate'
    },
    'hygiene_standards': {
        'inspection_frequency': 'daily',
        'minimum_score': 90,
        'certification_required': True
    },
    'documentation': {
        'required_records': [
            'temperature_logs',
            'cleaning_schedules',
            'staff_training',
            'pest_control'
        ],
        'retention_period': '3 years'
    }
}

# Food Safety Keywords
FOOD_SAFETY_KEYWORDS = [
    'HACCP',
    'food safety',
    'contamination',
    'allergen',
    'sanitization',
    'cold chain',
    'temperature control',
    'hygiene',
    'cross-contamination',
    'food handling',
]

# Document Types
DOCUMENT_TYPES = {
    'contracts': ['sla', 'service agreement', 'vendor contract'],
    'certifications': ['haccp', 'iso', 'food safety certification'],
    'inspections': ['health inspection', 'quality audit', 'safety assessment'],
    'training': ['food handler certification', 'safety training', 'hygiene course'],
}

# API Settings
API_URL = "http://localhost:8000"
REFRESH_INTERVAL = 5  # seconds
MAX_LIVE_ENTRIES = 10
TEMPERATURE_MIN = 2.0
TEMPERATURE_MAX = 8.0
QUALITY_THRESHOLD = 85 
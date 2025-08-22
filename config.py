"""Configuration settings for SCANA-AI."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = "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"
GPT_MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 1000

# Industry Configuration
SUPPORTED_INDUSTRIES = [
    "Food",
    "Pharma",
    "Retail",
    "BFSI",
    "Logistics"
]

# Email Configuration (from environment variables)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Webhook Configuration
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

# SMS Configuration
SMS_PROVIDER_API_KEY = os.getenv("SMS_PROVIDER_API_KEY", "")
SMS_SENDER_ID = os.getenv("SMS_SENDER_ID", "SCANA-AI")

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

# Compliance Categories
COMPLIANCE_CATEGORIES = {
    'food_safety': [
        'temperature_control',
        'hygiene_standards',
        'cross_contamination',
        'pest_control',
    ],
    'quality_assurance': [
        'product_freshness',
        'packaging_integrity',
        'labeling_accuracy',
        'shelf_life_compliance',
    ],
    'delivery_performance': [
        'on_time_delivery',
        'order_accuracy',
        'vehicle_condition',
        'staff_certification',
    ],
}

# Risk Levels and Scoring
RISK_SCORING = {
    'critical': {
        'weight': 5,
        'threshold': 95,
        'action': 'immediate_action_required',
    },
    'major': {
        'weight': 3,
        'threshold': 90,
        'action': 'corrective_action_needed',
    },
    'minor': {
        'weight': 1,
        'threshold': 85,
        'action': 'monitoring_required',
    },
}

# Industry-specific Keywords
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
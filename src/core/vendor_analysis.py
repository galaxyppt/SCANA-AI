"""Vendor analysis module with Indian market context."""

from datetime import datetime
import pandas as pd
import numpy as np
from .config import (
    TEMPERATURE_RANGES,
    QUALITY_THRESHOLDS,
    VENDOR_CATEGORIES,
    REGIONAL_REQUIREMENTS,
    FOOD_SAFETY_STANDARDS
)

class VendorRiskProfile:
    """Vendor risk profiling with Indian market context."""
    
    def __init__(self, vendor_data):
        # Create a deep copy of the DataFrame to avoid warnings
        self.vendor_data = vendor_data.copy()
        self.vendor_name = vendor_data['vendor_name'].iloc[0]
        self.risk_score = None
        self.category = self._determine_vendor_category()
        self.region = self._determine_region()
        
    def _determine_vendor_category(self):
        """Determine vendor category based on name and patterns."""
        for category, vendors in VENDOR_CATEGORIES.items():
            for vendor_type in vendors:
                if vendor_type.lower() in self.vendor_name.lower():
                    return category
        return 'general'
        
    def _determine_region(self):
        """Determine vendor's region based on data patterns."""
        # This would be enhanced with actual location data
        return 'north_india'  # Default for now
        
    def get_risk_score(self):
        """Calculate comprehensive risk score."""
        if self.risk_score is None:
            temp_risk = self.calculate_temperature_risk()
            quality_risk = self.calculate_quality_risk()
            timing_risk = self.calculate_timing_risk()
            compliance_risk = self.calculate_compliance_risk()
            
            # Weights adjusted for Indian market priorities
            weights = {
                'temperature': 0.35,  # Critical in Indian climate
                'quality': 0.25,      # Important for food safety
                'timing': 0.20,       # Delivery performance
                'compliance': 0.20    # Regulatory compliance
            }
            
            self.risk_score = (
                temp_risk * weights['temperature'] +
                quality_risk * weights['quality'] +
                timing_risk * weights['timing'] +
                compliance_risk * weights['compliance']
            )
        
        return self.risk_score
        
    def calculate_temperature_risk(self):
        """Calculate temperature risk considering regional factors."""
        if self.vendor_data.empty:
            return 100.0
            
        # Get regional requirements
        regional_reqs = REGIONAL_REQUIREMENTS.get(self.region, {})
        season = self._determine_season()
        
        # Adjust temperature thresholds based on region and season
        temp_range = TEMPERATURE_RANGES.get(self.category, TEMPERATURE_RANGES['cold_chain'])
        if season == 'summer' and 'summer' in regional_reqs:
            temp_range = {**temp_range, **regional_reqs['summer']}
        
        violations = self.vendor_data[
            (self.vendor_data['delivery_temperature'] < temp_range['min']) |
            (self.vendor_data['delivery_temperature'] > temp_range['max'])
        ]
        
        return 100 - (len(violations) / len(self.vendor_data) * 100)
        
    def calculate_quality_risk(self):
        """Calculate quality risk score."""
        if self.vendor_data.empty:
            return 100.0
            
        threshold = QUALITY_THRESHOLDS['critical'] if self.category in ['dairy_suppliers', 'quick_service'] else QUALITY_THRESHOLDS['major']
        
        violations = self.vendor_data[
            self.vendor_data['product_quality_score'] < threshold
        ]
        
        return 100 - (len(violations) / len(self.vendor_data) * 100)
        
    def calculate_timing_risk(self):
        """Calculate delivery timing risk."""
        if self.vendor_data.empty:
            return 100.0
            
        # Convert delivery_date and delivery_time to datetime
        try:
            # First ensure delivery_date is datetime
            if not pd.api.types.is_datetime64_any_dtype(self.vendor_data['delivery_date']):
                self.vendor_data.loc[:, 'delivery_date'] = pd.to_datetime(self.vendor_data['delivery_date'])
            
            # Convert delivery_time to string if it's not already
            self.vendor_data.loc[:, 'delivery_time'] = self.vendor_data['delivery_time'].astype(str)
            
            # Combine date and time
            self.vendor_data.loc[:, 'delivery_datetime'] = pd.to_datetime(
                self.vendor_data['delivery_date'].dt.strftime('%Y-%m-%d') + ' ' + self.vendor_data['delivery_time']
            )
        except Exception as e:
            print(f"Error in datetime conversion: {str(e)}")
            return 0.0  # Return worst score on error
        
        # Calculate delays and early deliveries
        total_deliveries = len(self.vendor_data)
        
        # Use delivery_status if available, otherwise use time_status
        if 'delivery_status' in self.vendor_data.columns:
            delayed = len(self.vendor_data[self.vendor_data['delivery_status'] == 'delayed'])
            early = len(self.vendor_data[self.vendor_data['delivery_status'] == 'early'])
        else:
            # Fallback to time_status
            delayed = len(self.vendor_data[self.vendor_data['time_status'] == 'Violation'])
            early = 0  # Can't determine early deliveries from time_status alone
        
        # Weighted score (delays are more serious than early deliveries)
        score = 100 - ((delayed * 1.5 + early * 0.5) / total_deliveries * 100)
        return max(0, min(100, score))
        
    def calculate_violation_frequency(self):
        """Calculate the frequency of violations."""
        if self.vendor_data.empty:
            return 0.0
            
        total_deliveries = len(self.vendor_data)
        violations = len(self.vendor_data[
            (self.vendor_data['temperature_status'] == 'Violation') |
            (self.vendor_data['time_status'] == 'Violation') |
            (self.vendor_data['quality_status'] == 'Violation')
        ])
        
        return (violations / total_deliveries) * 100
        
    def calculate_compliance_risk(self):
        """Calculate compliance risk based on Indian regulations."""
        # This would be enhanced with actual compliance data
        return 90.0  # Default for now
        
    def get_risk_category(self):
        """Get risk category with appropriate emoji."""
        score = self.get_risk_score()
        
        if score >= 90:
            return "Low Risk", "🟢"
        elif score >= 75:
            return "Medium Risk", "🟡"
        else:
            return "High Risk", "🔴"
            
    def _determine_season(self):
        """Determine current season for temperature adjustments."""
        month = datetime.now().month
        if 3 <= month <= 6:
            return 'summer'
        elif 7 <= month <= 9:
            return 'monsoon'
        else:
            return 'winter'
            
    def get_improvement_recommendations(self):
        """Get context-aware improvement recommendations."""
        score = self.get_risk_score()
        recommendations = []
        
        if score < 90:
            if self.calculate_temperature_risk() < 95:
                recommendations.append({
                    'category': 'Temperature Control',
                    'risk_level': 'High',
                    'recommendation': 'Implement continuous temperature monitoring system',
                    'impact': 'Prevent food spoilage and ensure safety'
                })
                
            if self.calculate_quality_risk() < 95:
                recommendations.append({
                    'category': 'Quality Assurance',
                    'risk_level': 'Medium',
                    'recommendation': 'Enhance quality inspection protocols',
                    'impact': 'Improve product quality and customer satisfaction'
                })
                
            if self.calculate_timing_risk() < 90:
                recommendations.append({
                    'category': 'Delivery Performance',
                    'risk_level': 'Medium',
                    'recommendation': 'Optimize delivery routes and timing',
                    'impact': 'Better delivery performance and customer satisfaction'
                })
                
        return recommendations

def analyze_vendor_trends(df):
    """Analyze vendor performance trends."""
    # Create a copy of the DataFrame
    df = df.copy()
    
    trends = {
        'daily_violations': pd.DataFrame(),
        'quality_trend': pd.DataFrame(),
        'temperature_compliance': pd.DataFrame()
    }
    
    # Convert dates
    df.loc[:, 'delivery_date'] = pd.to_datetime(df['delivery_date'])
    
    # Daily violations
    daily_violations = df.groupby(['delivery_date', 'vendor_name', 'overall_status']).size().unstack(fill_value=0)
    trends['daily_violations'] = daily_violations.reset_index()
    
    # Quality trend
    quality_trend = df.groupby(['delivery_date', 'vendor_name'])['product_quality_score'].mean().reset_index()
    trends['quality_trend'] = quality_trend
    
    # Temperature compliance
    temp_compliance = df.groupby(['delivery_date', 'vendor_name'])['temperature_status'].value_counts().unstack(fill_value=0)
    trends['temperature_compliance'] = temp_compliance.reset_index()
    
    return trends

def generate_vendor_summary(df):
    """Generate vendor performance summary with Indian context."""
    # Create a copy of the DataFrame
    df = df.copy()
    summary = []
    
    for vendor in df['vendor_name'].unique():
        vendor_data = df[df['vendor_name'] == vendor].copy()
        risk_profile = VendorRiskProfile(vendor_data)
        
        summary.append({
            'Vendor Name': vendor,
            'Category': risk_profile._determine_vendor_category(),
            'Region': risk_profile._determine_region(),
            'Risk Score': round(risk_profile.get_risk_score(), 1),
            'Temperature Compliance %': round(risk_profile.calculate_temperature_risk(), 1),
            'Quality Score': round(risk_profile.calculate_quality_risk(), 1),
            'Delivery Performance %': round(risk_profile.calculate_timing_risk(), 1),
            'FSSAI Compliance': 'Yes' if risk_profile.calculate_compliance_risk() > 90 else 'Review Required'
        })
    
    return pd.DataFrame(summary)

def identify_fraud_indicators(df):
    """Identify potential fraud indicators in delivery data."""
    # Create a copy of the DataFrame
    df = df.copy()
    indicators = []
    
    for vendor in df['vendor_name'].unique():
        vendor_data = df[df['vendor_name'] == vendor].copy()
        
        # Check for temperature tampering
        temp_std = vendor_data['delivery_temperature'].std()
        if temp_std < 0.1:  # Suspiciously consistent temperatures
            indicators.append({
                'vendor': vendor,
                'type': 'Temperature Data Anomaly',
                'description': 'Unusually consistent temperature readings suggest possible data manipulation'
            })
        
        # Check for time clustering
        try:
            # Convert delivery_date and delivery_time to datetime
            vendor_data.loc[:, 'delivery_datetime'] = pd.to_datetime(
                vendor_data['delivery_date'].astype(str) + ' ' + vendor_data['delivery_time'].astype(str)
            )
            time_diffs = vendor_data['delivery_datetime'].diff()
            if len(time_diffs) > 1 and time_diffs.value_counts().iloc[0] > len(vendor_data) * 0.5:
                indicators.append({
                    'vendor': vendor,
                    'type': 'Delivery Time Pattern',
                    'description': 'Suspicious pattern in delivery timing suggests possible log manipulation'
                })
        except Exception as e:
            print(f"Warning: Could not analyze time patterns for vendor {vendor}: {str(e)}")
        
        # Check for quality score patterns
        quality_std = vendor_data['product_quality_score'].std()
        if quality_std < 0.5:  # Too consistent quality scores
            indicators.append({
                'vendor': vendor,
                'type': 'Quality Score Anomaly',
                'description': 'Unusually consistent quality scores suggest possible reporting issues'
            })
    
    return indicators 
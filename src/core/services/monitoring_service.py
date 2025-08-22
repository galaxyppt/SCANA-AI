"""Service for real-time delivery monitoring and breach detection."""

from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime
from ..persistence.data_store import DataStore

class MonitoringService:
    """Service for monitoring deliveries and detecting breaches."""
    
    def __init__(self, data_store: Optional[DataStore] = None):
        """
        Initialize the monitoring service.
        
        Args:
            data_store: Optional DataStore instance for persistence
        """
        self.data_store = data_store or DataStore()
        self.current_data = pd.DataFrame()
        self.violation_count = {
            'temperature': 0,
            'quality': 0,
            'timing': 0
        }
        self.last_update = None
    
    def update_delivery_data(self, new_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Update delivery data and check for violations.
        
        Args:
            new_data: New delivery records
            
        Returns:
            dict: Update results including violations
        """
        try:
            # Append new data
            self.current_data = pd.concat([self.current_data, new_data], ignore_index=True)
            
            # Check for violations
            violations = self._check_violations(new_data)
            
            # Update violation counts
            for violation_type, count in violations['counts'].items():
                self.violation_count[violation_type] += count
            
            # Update timestamp
            self.last_update = datetime.now()
            
            # Save data if store available
            if self.data_store:
                self.data_store.save_delivery_data(self.current_data)
            
            return {
                'status': 'success',
                'violations': violations,
                'total_records': len(self.current_data),
                'new_records': len(new_data)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _check_violations(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Check for violations in delivery data."""
        violations = {
            'records': [],
            'counts': {
                'temperature': 0,
                'quality': 0,
                'timing': 0
            }
        }
        
        for _, delivery in data.iterrows():
            record_violations = []
            
            # Check temperature
            if not (2.0 <= delivery['delivery_temperature'] <= 8.0):
                record_violations.append('temperature')
                violations['counts']['temperature'] += 1
            
            # Check quality
            if delivery['product_quality_score'] < 85:
                record_violations.append('quality')
                violations['counts']['quality'] += 1
            
            # Check timing (if status available)
            if 'delivery_status' in delivery and delivery['delivery_status'] == 'delayed':
                record_violations.append('timing')
                violations['counts']['timing'] += 1
            
            if record_violations:
                violations['records'].append({
                    'vendor': delivery['vendor_name'],
                    'date': delivery['delivery_date'],
                    'violations': record_violations
                })
        
        return violations
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """
        Get current monitoring statistics.
        
        Returns:
            dict: Monitoring statistics and metrics
        """
        if self.current_data.empty:
            return {
                'status': 'no_data',
                'message': 'No delivery data available'
            }
        
        total_deliveries = len(self.current_data)
        total_violations = sum(self.violation_count.values())
        
        return {
            'status': 'active',
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'total_deliveries': total_deliveries,
            'total_violations': total_violations,
            'compliance_rate': (
                (total_deliveries - total_violations) / total_deliveries * 100
                if total_deliveries > 0 else 100
            ),
            'violation_breakdown': self.violation_count
        }
    
    def get_vendor_performance(self, vendor_name: str) -> Dict[str, Any]:
        """
        Get performance metrics for a specific vendor.
        
        Args:
            vendor_name: Name of the vendor
            
        Returns:
            dict: Vendor performance metrics
        """
        if self.current_data.empty:
            return {
                'status': 'no_data',
                'message': 'No delivery data available'
            }
        
        vendor_data = self.current_data[self.current_data['vendor_name'] == vendor_name]
        if vendor_data.empty:
            return {
                'status': 'not_found',
                'message': f'No data found for vendor: {vendor_name}'
            }
        
        violations = self._check_violations(vendor_data)
        total_violations = sum(violations['counts'].values())
        
        return {
            'status': 'success',
            'total_deliveries': len(vendor_data),
            'total_violations': total_violations,
            'compliance_rate': (
                (len(vendor_data) - total_violations) / len(vendor_data) * 100
                if len(vendor_data) > 0 else 100
            ),
            'violation_breakdown': violations['counts'],
            'average_temperature': vendor_data['delivery_temperature'].mean(),
            'average_quality_score': vendor_data['product_quality_score'].mean()
        }
    
    def clear_monitoring_data(self) -> bool:
        """
        Clear all monitoring data.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.current_data = pd.DataFrame()
            self.violation_count = {
                'temperature': 0,
                'quality': 0,
                'timing': 0
            }
            self.last_update = None
            
            if self.data_store:
                self.data_store.clear_data()
            
            return True
        except Exception as e:
            print(f"Error clearing monitoring data: {str(e)}")
            return False 
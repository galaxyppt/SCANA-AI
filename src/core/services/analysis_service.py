"""Service layer for integrating document processing and analysis."""

from typing import Dict, Any, Optional, List
try:
    from ..document.pdf_processor import PDFProcessor
    HAS_PDF_PROCESSOR = True
except ImportError:
    HAS_PDF_PROCESSOR = False
from ..document.gpt_analyzer import GPTAnalyzer
import pandas as pd
from datetime import datetime

class AnalysisService:
    """Service for analyzing contracts and delivery data."""
    
    def __init__(self):
        """Initialize the analysis service with required components."""
        self.pdf_processor = PDFProcessor() if HAS_PDF_PROCESSOR else None
        self.gpt_analyzer = GPTAnalyzer()
        self.last_analysis = None
    
    def analyze_contract(self, contract_file) -> Dict[str, Any]:
        """Analyze a contract file and extract SLA terms."""
        try:
            # Extract text from contract file
            if hasattr(contract_file, 'read'):
                # If it's a file-like object (e.g., from Streamlit uploader)
                if self.pdf_processor and contract_file.name.lower().endswith('.pdf'):
                    text = self.pdf_processor.extract_text(contract_file)
                else:
                    # For text files or fallback
                    text = contract_file.read().decode('utf-8')
            else:
                # If it's a file path
                if self.pdf_processor and contract_file.lower().endswith('.pdf'):
                    text = self.pdf_processor.extract_text(contract_file)
                else:
                    with open(contract_file, 'r', encoding='utf-8') as f:
                        text = f.read()
            
            # Use GPT analyzer to extract SLA clauses
            sla_analysis = self.gpt_analyzer.extract_sla_terms(text)
            
            # If we got structured clauses from the analyzer
            if isinstance(sla_analysis, dict) and 'clauses' in sla_analysis:
                clauses = sla_analysis['clauses']
            else:
                # Convert old format or handle error
                clauses = sla_analysis if isinstance(sla_analysis, list) else []
            
            # Create metadata
            metadata = {
                "analyzed_at": datetime.now().isoformat(),
                "text_length": len(text),
                "clauses_found": len(clauses)
            }
            
            # Store the analysis for later reference
            self.last_analysis = {
                "clauses": clauses,
                "metadata": metadata,
                "text_length": len(text)
            }
            
            return {
                "clauses": clauses,
                "metadata": metadata
            }
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_delivery_data(self, delivery_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze delivery performance data."""
        try:
            if delivery_data.empty:
                return {"error": "No data provided"}
                
            analysis = {
                "total_deliveries": len(delivery_data),
                "avg_temperature": delivery_data["delivery_temperature"].mean() if "delivery_temperature" in delivery_data.columns else None,
                "avg_quality": delivery_data["product_quality_score"].mean() if "product_quality_score" in delivery_data.columns else None,
                "analyzed_at": datetime.now().isoformat()
            }
            
            return analysis
        except Exception as e:
            return {"error": str(e)}
    
    def get_summary_report(self) -> Dict[str, Any]:
        """
        Generate a summary report of the last analysis.
        
        Returns:
            dict: Summary report
        """
        if not self.last_analysis:
            return {'error': 'No analysis available'}
        
        return {
            'document_info': {
                'pages': self.last_analysis['metadata'].get('pages', 0),
                'text_length': self.last_analysis['text_length']
            },
            'sla_terms': {
                'count': len(self.last_analysis['sla_terms']),
                'types': [term['type'] for term in self.last_analysis['sla_terms']]
            }
        }
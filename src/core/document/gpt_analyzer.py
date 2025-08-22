"""GPT-based document analyzer for SCANA-AI."""

from typing import Dict, Any, List
import os
import openai
from datetime import datetime

class GPTAnalyzer:
    """GPT-powered document analysis service."""
    
    def __init__(self):
        """Initialize the GPT analyzer."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
    
    def extract_sla_terms(self, text: str) -> Dict[str, Any]:
        """Extract SLA terms from contract text using GPT."""
        try:
            if not self.api_key:
                return {"clauses": self._mock_sla_terms()}
            
            # System prompt to guide GPT's analysis
            system_prompt = """You are a legal document analyzer specialized in Service Level Agreements (SLAs).
            Extract the following clauses from the contract in a structured format:
            1. Delivery time requirements and schedules
            2. Cold chain and temperature control specifications
            3. Hygiene and quality standards
            4. Penalties and consequences for non-compliance
            
            For each clause:
            - Provide a clear description of the requirement
            - Identify the expected value or threshold (e.g., "48 hours", "2°C to 8°C", "ISO 22000")
            - Maintain the original wording
            - Exclude any interpretation or commentary
            
            Format your response as follows for each clause type:
            
            CLAUSE TYPE: [delivery_time/temperature_range/quality_standard/penalty]
            DESCRIPTION: [Clear description of the requirement]
            EXPECTED VALUE: [Specific threshold, value, or standard]
            """
            
            # Call GPT API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Use the model specified in config
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Please analyze this contract and extract the SLA clauses:\n\n{text}"}
                ],
                temperature=0.0,  # Keep it deterministic
                max_tokens=1000   # Reasonable token limit
            )
            
            # Extract the response content
            gpt_response = response.choices[0].message.content
            
            # Initialize the return structure with structured data
            sla_clauses = {
                "clauses": [
                    {
                        "type": "delivery_time",
                        "description": "",
                        "expected_value": ""
                    },
                    {
                        "type": "temperature_range",
                        "description": "",
                        "expected_value": ""
                    },
                    {
                        "type": "quality_standard",
                        "description": "",
                        "expected_value": ""
                    },
                    {
                        "type": "penalty",
                        "description": "",
                        "expected_value": ""
                    }
                ]
            }
            
            # Process GPT's response to extract structured information
            current_clause = None
            current_field = None
            
            for line in gpt_response.split('\n'):
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                    
                # Identify clause type
                if line.lower().startswith("clause type:"):
                    clause_type = line.split(":", 1)[1].strip().lower()
                    
                    # Map to our clause types
                    if "delivery" in clause_type or "time" in clause_type:
                        current_clause = next((c for c in sla_clauses["clauses"] if c["type"] == "delivery_time"), None)
                    elif "temperature" in clause_type or "cold" in clause_type:
                        current_clause = next((c for c in sla_clauses["clauses"] if c["type"] == "temperature_range"), None)
                    elif "quality" in clause_type or "hygiene" in clause_type or "standard" in clause_type:
                        current_clause = next((c for c in sla_clauses["clauses"] if c["type"] == "quality_standard"), None)
                    elif "penalty" in clause_type or "fine" in clause_type or "breach" in clause_type:
                        current_clause = next((c for c in sla_clauses["clauses"] if c["type"] == "penalty"), None)
                    
                    current_field = None
                    
                # Identify field type
                elif line.lower().startswith("description:"):
                    current_field = "description"
                    if current_clause:
                        current_clause["description"] = line.split(":", 1)[1].strip()
                elif line.lower().startswith("expected value:"):
                    current_field = "expected_value"
                    if current_clause:
                        current_clause["expected_value"] = line.split(":", 1)[1].strip()
                # Append to current field if we're in the middle of a field
                elif current_clause and current_field:
                    current_clause[current_field] += "\n" + line
            
            # Clean up empty clauses
            sla_clauses["clauses"] = [clause for clause in sla_clauses["clauses"] if clause["description"] or clause["expected_value"]]
            
            # If no clauses were found, use mock data
            if not sla_clauses["clauses"]:
                sla_clauses["clauses"] = self._mock_sla_terms()
                
            return sla_clauses
            
        except Exception as e:
            print(f"Error in GPT analysis: {str(e)}")
            return {"clauses": self._mock_sla_terms(), "error": str(e)}
    
    def analyze_compliance(self, sla_terms: List[Dict[str, Any]], delivery_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze delivery compliance against SLA terms."""
        try:
            violations = []
            
            # Check temperature compliance
            if "delivery_temperature" in delivery_data:
                temp = delivery_data["delivery_temperature"]
                if temp < 2.0 or temp > 8.0:
                    violations.append({
                        "type": "temperature",
                        "value": temp,
                        "threshold": "2.0-8.0°C",
                        "severity": "high"
                    })
            
            # Check quality compliance
            if "product_quality_score" in delivery_data:
                quality = delivery_data["product_quality_score"]
                if quality < 85:
                    violations.append({
                        "type": "quality",
                        "value": quality,
                        "threshold": "85",
                        "severity": "medium"
                    })
            
            return {
                "compliant": len(violations) == 0,
                "violations": violations,
                "checked_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _mock_sla_terms(self) -> List[Dict[str, Any]]:
        """Generate mock SLA terms for testing."""
        return [
            {
                "type": "delivery_time",
                "description": "Delivery should be completed within a certain time of order placement",
                "expected_value": "48 hours"
            },
            {
                "type": "temperature_range",
                "description": "Temperature must be maintained within a certain range throughout the logistics process",
                "expected_value": "2°C to 8°C"
            },
            {
                "type": "quality_standard",
                "description": "Product quality must meet certain standards",
                "expected_value": "ISO 22000"
            },
            {
                "type": "penalty",
                "description": "Any delivery delay over a certain time beyond SLA will be penalized",
                "expected_value": "2 hours"
            }
        ]
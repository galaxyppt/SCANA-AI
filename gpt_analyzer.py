"""
GPT-powered contract analysis module for SCANA-AI.
Extracts SLA clauses from contracts using OpenAI's GPT models.
"""

import openai
from typing import Dict, Optional
from config import OPENAI_API_KEY, GPT_MODEL, MAX_TOKENS

# Configure OpenAI
openai.api_key = OPENAI_API_KEY

def extract_sla_clauses(text: str) -> Dict[str, Any]:
    """
    Extract SLA clauses from contract text using GPT.
    
    Args:
        text (str): Plain text contract document
        
    Returns:
        Dict[str, Any]: Dictionary containing extracted SLA clauses with descriptions and expected values
    """
    
    # System prompt to guide GPT's analysis
    system_prompt = """You are a legal document analyzer specialized in Service Level Agreements (SLAs).
    Extract the following clauses from the contract in a structured format:
    1. Delivery time requirements and schedules
    2. Cold chain and temperature control specifications
    3. Hygiene and quality standards
    4. Penalties and consequences for non-compliance
    
    For each clause:
    - Extract the exact text from the contract
    - Provide a clear description of the requirement
    - Identify the expected value or threshold (e.g., "48 hours", "2°C to 8°C", "ISO 22000")
    - Maintain the original wording
    - Exclude any interpretation or commentary
    
    Format your response as follows for each clause type:
    
    CLAUSE TYPE: [delivery_time/temperature_range/quality_standard/penalty]
    DESCRIPTION: [Clear description of the requirement]
    EXPECTED VALUE: [Specific threshold, value, or standard]
    """

    try:
        # Call GPT API
        response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please analyze this contract and extract the SLA clauses:\n\n{text}"}
            ],
            temperature=0.0,  # Keep it deterministic
            max_tokens=MAX_TOKENS
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
        
        return sla_clauses

    except Exception as e:
        print(f"Error in GPT analysis: {str(e)}")
        return {
            "delivery_time": "",
            "cold_chain_requirement": "",
            "hygiene_standards": "",
            "penalties": "",
            "error": str(e)
        }
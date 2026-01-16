import requests
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class OllamaService:
    """Service for integrating with local Ollama LLM."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "mistral:instruct"
    
    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
            return False
    
    def analyze_evidence_candidate(
        self, 
        control_id: str,
        control_name: str,
        control_text: str,
        candidate_text: str
    ) -> Dict[str, Any]:
        """
        Analyze if a text chunk is relevant evidence for a NIST CSF control.
        
        Returns:
        {
            "is_relevant": bool,
            "confidence": float (0-1),
            "evidence_type": str (policy|procedure|technical|operational),
            "reasoning": str,
            "key_phrases": list[str]
        }
        """
        if not self.is_available():
            return {"error": "Ollama not available"}
        
        prompt = f"""You are a cybersecurity auditor analyzing evidence for NIST CSF 2.0 compliance.

Control: {control_id} - {control_name}
Description: {control_text}

Evidence Text:
{candidate_text[:2000]}

Analyze if this text is relevant evidence for this control. Respond in this exact JSON format:
{{
  "is_relevant": true/false,
  "confidence": 0.0-1.0,
  "evidence_type": "policy|procedure|technical|operational",
  "reasoning": "brief explanation",
  "key_phrases": ["phrase1", "phrase2"]
}}

Rules:
- policy: written policies, standards, governance documents
- procedure: step-by-step procedures, processes, workflows
- technical: system configs, logs, security controls, technical implementations
- operational: training records, audit results, evidence of activities

Be strict. Only mark as relevant if it DIRECTLY addresses this control."""

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.1,  # Low temp for consistency
                        "top_p": 0.9
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # Parse the JSON response from the model
                import json
                analysis = json.loads(result.get("response", "{}"))
                return analysis
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return {"error": "Ollama request failed"}
                
        except Exception as e:
            logger.error(f"Ollama analysis failed: {e}")
            return {"error": str(e)}

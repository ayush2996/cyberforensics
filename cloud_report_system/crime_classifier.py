# crime_classifier.py
from llm_manager import llm
from prompts import CRIME_TYPE_DETECTION_PROMPT
from models import CrimeType, CrimeTypeSelectionResponse
import json
from typing import Dict, List, Tuple

class CrimeClassifier:
    """Classifies incidents into cyber crime categories"""
    
    def __init__(self):
        self.crime_types = list(CrimeType)
        self.llm = llm
    
    def classify_incident(self, description: str) -> CrimeTypeSelectionResponse:
        """
        Classify an incident into crime categories using LLM
        
        Args:
            description: Brief description of the incident
            
        Returns:
            CrimeTypeSelectionResponse with detected types and confidence
        """
        try:
            prompt = CRIME_TYPE_DETECTION_PROMPT.format(description=description)
            
            system_prompt = """You are a cybercrime classification expert. 
Your job is to accurately classify incidents into specific crime categories.
Respond ONLY with valid JSON, no additional text."""
            
            response = self.llm.generate(prompt, system_prompt, max_tokens=500)
            
            # Parse the JSON response
            result = json.loads(response)
            
            # Validate and normalize crime types
            detected_types = []
            for crime_type in result.get("detected_types", []):
                try:
                    detected_types.append(CrimeType(crime_type.lower()))
                except ValueError:
                    # Skip invalid crime types
                    pass
            
            if not detected_types:
                detected_types = [CrimeType.FRAUD]  # Default fallback
            
            primary_type = detected_types[0]
            confidence = min(result.get("confidence", 0.7), 1.0)
            reasoning = result.get("reasoning", "Classification based on incident description")
            
            return CrimeTypeSelectionResponse(
                status="success",
                detected_types=detected_types,
                confidence=confidence,
                recommendation=primary_type,
                message=reasoning
            )
        
        except json.JSONDecodeError:
            # Fallback if LLM doesn't return valid JSON
            return self._fallback_classification(description)
        except Exception as e:
            print(f"Error in crime classification: {e}")
            return self._fallback_classification(description)
    
    def _fallback_classification(self, description: str) -> CrimeTypeSelectionResponse:
        """Fallback classification when LLM fails"""
        keywords_map = {
            CrimeType.PHISHING: ["phishing", "email", "credential", "link", "click"],
            CrimeType.RANSOMWARE: ["ransomware", "encrypted", "ransom", "note"],
            CrimeType.DATA_BREACH: ["breach", "data", "unauthorized access", "stolen"],
            CrimeType.IDENTITY_THEFT: ["identity", "ssn", "credit", "fraud account"],
            CrimeType.FRAUD: ["fraud", "scam", "money", "transfer"],
            CrimeType.MALWARE: ["malware", "virus", "infection", "antivirus"],
            CrimeType.DDoS: ["ddos", "attack", "service", "unavailable"],
            CrimeType.HACKING: ["hacking", "unauthorized access", "breach"],
            CrimeType.EXTORTION: ["extortion", "threat", "payment", "blackmail"],
            CrimeType.SPAM: ["spam", "unsolicited", "message"],
        }
        
        desc_lower = description.lower()
        detected_types = []
        
        for crime_type, keywords in keywords_map.items():
            if any(keyword in desc_lower for keyword in keywords):
                detected_types.append(crime_type)
        
        if not detected_types:
            detected_types = [CrimeType.FRAUD]
        
        return CrimeTypeSelectionResponse(
            status="success",
            detected_types=detected_types,
            confidence=0.6,
            recommendation=detected_types[0],
            message="Classification based on keyword matching"
        )
    
    def get_crime_model(self, crime_type: CrimeType):
        """Get the Pydantic model for a specific crime type"""
        from models import (
            PhishingReport, RansomwareReport, DataBreachReport,
            IdentityTheftReport, FraudReport, MalwareReport,
            DDoSReport, HackingReport, ExtortionReport, SpamReport
        )
        
        model_map = {
            CrimeType.PHISHING: PhishingReport,
            CrimeType.RANSOMWARE: RansomwareReport,
            CrimeType.DATA_BREACH: DataBreachReport,
            CrimeType.IDENTITY_THEFT: IdentityTheftReport,
            CrimeType.FRAUD: FraudReport,
            CrimeType.MALWARE: MalwareReport,
            CrimeType.DDoS: DDoSReport,
            CrimeType.HACKING: HackingReport,
            CrimeType.EXTORTION: ExtortionReport,
            CrimeType.SPAM: SpamReport,
        }
        
        return model_map.get(crime_type, FraudReport)

# Export singleton instance
crime_classifier = CrimeClassifier()


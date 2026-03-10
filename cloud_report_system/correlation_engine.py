# correlation_engine.py
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from llm_manager import llm
from prompts import CORRELATION_CHECK_PROMPT, CORRELATION_SEARCH_PROMPT
from models import CorrelationResult, CrimeType
import json
import re

class CorrelationEngine:
    """Analyzes incidents for correlations with known patterns and previous cases"""
    
    def __init__(self):
        self.llm = llm
        # Simulated case database (in production, this would be a real database)
        self.case_database = []
        self.known_patterns = []
        self.known_contacts = {}  # email/phone -> case_ids mapping
    
    async def analyze_correlation(self, current_incident: Dict[str, Any], 
                                  crime_type: CrimeType) -> CorrelationResult:
        """
        Analyze if current incident correlates with previous cases
        
        Args:
            current_incident: The incident data to analyze
            crime_type: Type of crime
            
        Returns:
            CorrelationResult with findings
        """
        correlation_result = CorrelationResult()
        
        try:
            # Extract searchable fields from incident
            extracted_fields = self._extract_correlation_fields(current_incident, crime_type)
            
            # Search for similar cases
            similar_cases = await self._search_similar_cases(extracted_fields, crime_type)
            
            if similar_cases:
                correlation_result.similar_cases = similar_cases
                correlation_result.status = "correlated"
                
                # Analyze patterns
                patterns = self._analyze_patterns(similar_cases, current_incident)
                correlation_result.matching_patterns = patterns["patterns"]
                correlation_result.matching_callers = patterns["contacts"]
                correlation_result.correlation_score = patterns["score"]
                
                # Extract case IDs
                correlation_result.correlated_case_ids = [
                    case.get("case_id", "") for case in similar_cases
                ]
                
                correlation_result.recommendation = self._generate_recommendation(
                    patterns, crime_type
                )
            else:
                correlation_result.status = "no_correlation"
                correlation_result.recommendation = "No correlations found. Case appears to be standalone."
            
            return correlation_result
        
        except Exception as e:
            print(f"Error in correlation analysis: {e}")
            correlation_result.status = "no_correlation"
            correlation_result.recommendation = "Unable to complete correlation analysis at this time."
            return correlation_result
    
    def _extract_correlation_fields(self, incident: Dict[str, Any], 
                                    crime_type: CrimeType) -> Dict[str, Any]:
        """Extract fields relevant for correlation from incident data"""
        extracted = {
            "crime_type": crime_type.value,
            "emails": [],
            "phone_numbers": [],
            "ip_addresses": [],
            "amounts": [],
            "keywords": [],
            "date_range": None
        }
        
        # Extract emails
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        for key, value in incident.items():
            if isinstance(value, str):
                extracted["emails"].extend(re.findall(email_pattern, value))
                extracted["keywords"].extend(value.lower().split())
        
        # Extract phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b|\b\d{10}\b'
        for key, value in incident.items():
            if isinstance(value, str):
                extracted["phone_numbers"].extend(re.findall(phone_pattern, value))
        
        # Extract amounts (for financial crimes)
        amount_pattern = r'\$[\d,.]+'
        for key, value in incident.items():
            if isinstance(value, (int, float)):
                extracted["amounts"].append(value)
            elif isinstance(value, str):
                extracted["amounts"].extend(re.findall(amount_pattern, value))
        
        # Extract IP addresses
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        for key, value in incident.items():
            if isinstance(value, str):
                extracted["ip_addresses"].extend(re.findall(ip_pattern, value))
        
        return extracted
    
    async def _search_similar_cases(self, extracted_fields: Dict[str, Any],
                                    crime_type: CrimeType) -> List[Dict[str, Any]]:
        """Search database for similar cases"""
        similar_cases = []
        
        # Search by exact matches first
        similar_cases.extend(
            self._find_cases_by_contact(extracted_fields["emails"], 
                                       extracted_fields["phone_numbers"])
        )
        
        # Search by crime type and temporal proximity
        similar_cases.extend(
            self._find_cases_by_type_and_date(crime_type)
        )
        
        # Remove duplicates while preserving order
        seen = set()
        unique_cases = []
        for case in similar_cases:
            case_id = case.get("case_id", "")
            if case_id not in seen:
                seen.add(case_id)
                unique_cases.append(case)
        
        return unique_cases[:5]  # Return top 5 matches
    
    def _find_cases_by_contact(self, emails: List[str], 
                               phones: List[str]) -> List[Dict[str, Any]]:
        """Find cases with matching emails or phone numbers"""
        matching_cases = []
        
        for email in emails:
            if email in self.known_contacts:
                for case_id in self.known_contacts[email]:
                    case = next(
                        (c for c in self.case_database if c.get("case_id") == case_id),
                        None
                    )
                    if case:
                        matching_cases.append(case)
        
        for phone in phones:
            if phone in self.known_contacts:
                for case_id in self.known_contacts[phone]:
                    case = next(
                        (c for c in self.case_database if c.get("case_id") == case_id),
                        None
                    )
                    if case:
                        matching_cases.append(case)
        
        return matching_cases
    
    def _find_cases_by_type_and_date(self, crime_type: CrimeType,
                                    days_back: int = 90) -> List[Dict[str, Any]]:
        """Find cases of same type within recent time period"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        matching_cases = []
        for case in self.case_database:
            if (case.get("crime_type") == crime_type.value and
                case.get("date_reported")):
                try:
                    case_date = datetime.fromisoformat(case["date_reported"])
                    if case_date > cutoff_date:
                        matching_cases.append(case)
                except:
                    pass
        
        return matching_cases
    
    def _analyze_patterns(self, similar_cases: List[Dict[str, Any]],
                         current_incident: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze common patterns between cases"""
        patterns = {
            "patterns": [],
            "contacts": [],
            "score": 0.0
        }
        
        if not similar_cases:
            return patterns
        
        # Check for common patterns
        common_patterns = set()
        total_score = 0
        
        for case in similar_cases:
            # Check same email
            if "emails" in case and "emails" in current_incident:
                common_emails = set(case.get("emails", [])) & set(current_incident.get("emails", []))
                if common_emails:
                    patterns["contacts"].extend(list(common_emails))
                    common_patterns.add("matching_email")
                    total_score += 0.3
            
            # Check same phone
            if "phone_numbers" in case and "phone_numbers" in current_incident:
                common_phones = set(case.get("phone_numbers", [])) & set(current_incident.get("phone_numbers", []))
                if common_phones:
                    patterns["contacts"].extend(list(common_phones))
                    common_patterns.add("matching_phone")
                    total_score += 0.3
            
            # Check similar amounts
            if "amount" in case and "amount" in current_incident:
                case_amt = case.get("amount", 0)
                incident_amt = current_incident.get("amount", 0)
                if case_amt and incident_amt:
                    ratio = min(case_amt, incident_amt) / max(case_amt, incident_amt)
                    if ratio > 0.7:  # Similar amounts
                        common_patterns.add("similar_amount")
                        total_score += 0.2
            
            # Check same attack vector
            if "attack_vector" in case and "attack_vector" in current_incident:
                if case.get("attack_vector") == current_incident.get("attack_vector"):
                    common_patterns.add("same_attack_vector")
                    total_score += 0.25
        
        patterns["patterns"] = list(common_patterns)
        patterns["score"] = min(total_score / len(similar_cases), 1.0)
        
        return patterns
    
    def _generate_recommendation(self, patterns: Dict[str, Any],
                                crime_type: CrimeType) -> str:
        """Generate investigation recommendation based on patterns"""
        if patterns["score"] > 0.7:
            if patterns["contacts"]:
                contacts_str = ", ".join(patterns["contacts"][:2])
                return f"HIGH CORRELATION FOUND: Same contacts ({contacts_str}) involved in previous cases. Recommend joint investigation task force."
            else:
                return "HIGH CORRELATION FOUND: Similar crime pattern detected. Recommend cross-referencing tactics and preventive measures."
        
        elif patterns["score"] > 0.4:
            return "MODERATE CORRELATION: Some similarities with previous cases. Recommend reviewing similar cases for patterns and methodology."
        
        else:
            return "No significant correlations found. However, case information has been added to database for future pattern matching."
    
    def add_case_to_database(self, case_data: Dict[str, Any], case_id: str):
        """Add a resolved case to the correlation database"""
        case_entry = {
            "case_id": case_id,
            "date_reported": datetime.now().isoformat(),
            **case_data
        }
        
        self.case_database.append(case_entry)
        
        # Index contacts for quick lookup
        for email in case_data.get("emails", []):
            if email not in self.known_contacts:
                self.known_contacts[email] = []
            self.known_contacts[email].append(case_id)
        
        for phone in case_data.get("phone_numbers", []):
            if phone not in self.known_contacts:
                self.known_contacts[phone] = []
            self.known_contacts[phone].append(case_id)

# Export singleton instance
correlation_engine = CorrelationEngine()


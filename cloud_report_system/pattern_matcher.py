# pattern_matcher.py
"""
Stage Three: Pattern Matching & Signal Detection
Analyzes text for specific "markers" unique to certain crime types.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
import re

@dataclass
class SignalPattern:
    """Pattern detection for crime signals"""
    name: str
    keywords: List[str]
    weight: float
    context: str

class PatternMatcher:
    """
    Detects crime-specific patterns and signals:
    - Keyword density
    - Platform context
    - Urgency/emotion signals
    - Technical indicators
    """
    
    def __init__(self):
        """Initialize signal patterns for each crime type"""
        self.signal_patterns = {
            "phishing": [
                SignalPattern(
                    name="credential_request",
                    keywords=["verify", "confirm", "login", "password", "authenticate", "credentials", "account"],
                    weight=0.25,
                    context="Request for credentials or verification"
                ),
                SignalPattern(
                    name="link_click",
                    keywords=["click", "link", "url", "button", "visit", "open"],
                    weight=0.20,
                    context="User clicked on suspicious link"
                ),
                SignalPattern(
                    name="fake_authority",
                    keywords=["bank", "paypal", "amazon", "apple", "microsoft", "official", "urgent", "immediately"],
                    weight=0.25,
                    context="Imperssonation of legitimate authority"
                ),
                SignalPattern(
                    name="email_platform",
                    keywords=["email", "gmail", "outlook", "yahoo", "icloud"],
                    weight=0.15,
                    context="Email delivery platform mentioned"
                ),
            ],
            "ransomware": [
                SignalPattern(
                    name="encryption",
                    keywords=["encrypted", "locked", "cannot open", "extension", "file", "encrypted files"],
                    weight=0.30,
                    context="Files are encrypted and inaccessible"
                ),
                SignalPattern(
                    name="ransom_demand",
                    keywords=["ransom", "pay", "bitcoin", "wallet", "cryptocurrency", "payment"],
                    weight=0.30,
                    context="Explicit ransom demand"
                ),
                SignalPattern(
                    name="deadline",
                    keywords=["hours", "days", "deadline", "timer", "soon", "expired", "before"],
                    weight=0.20,
                    context="Time pressure and deadline"
                ),
                SignalPattern(
                    name="note_file",
                    keywords=["note", "message", "readme", "instructions", "contact"],
                    weight=0.20,
                    context="Ransom note or instructions left"
                ),
            ],
            "identity_theft": [
                SignalPattern(
                    name="account_opened",
                    keywords=["account opened", "opened credit", "new account", "unauthorized account"],
                    weight=0.30,
                    context="Fraudulent accounts opened in victim's name"
                ),
                SignalPattern(
                    name="personal_info",
                    keywords=["ssn", "social security", "date of birth", "driver's license", "identity"],
                    weight=0.25,
                    context="Personal identifying information"
                ),
                SignalPattern(
                    name="credit_damage",
                    keywords=["credit", "credit score", "credit report", "credit inquiry", "credit card"],
                    weight=0.25,
                    context="Credit or financial impact"
                ),
                SignalPattern(
                    name="discovery",
                    keywords=["discovered", "found out", "realized", "noticed", "saw"],
                    weight=0.20,
                    context="How victim discovered the theft"
                ),
            ],
            "fraud": [
                SignalPattern(
                    name="money_loss",
                    keywords=["money", "dollars", "payment", "transfer", "sent", "lost", "amount"],
                    weight=0.30,
                    context="Financial loss mentioned"
                ),
                SignalPattern(
                    name="false_promise",
                    keywords=["investment", "return", "profit", "guaranteed", "promise", "opportunity"],
                    weight=0.25,
                    context="False promises or investment opportunities"
                ),
                SignalPattern(
                    name="wire_fraud",
                    keywords=["wire", "bank transfer", "credit card", "paypal", "venmo", "zelle"],
                    weight=0.25,
                    context="Payment method used"
                ),
                SignalPattern(
                    name="scammer_contact",
                    keywords=["phone", "email", "contacted", "called", "messaged", "communication"],
                    weight=0.20,
                    context="How attacker made contact"
                ),
            ],
            "malware": [
                SignalPattern(
                    name="infection",
                    keywords=["malware", "virus", "infected", "infection", "detected"],
                    weight=0.30,
                    context="Malware infection confirmed"
                ),
                SignalPattern(
                    name="antivirus",
                    keywords=["antivirus", "scanning", "quarantine", "blocked", "alert", "warning"],
                    weight=0.25,
                    context="Antivirus detection or alerts"
                ),
                SignalPattern(
                    name="system_behavior",
                    keywords=["slow", "crashing", "error", "pop-up", "strange", "unusual"],
                    weight=0.25,
                    context="Unusual system behavior"
                ),
                SignalPattern(
                    name="data_access",
                    keywords=["accessed", "data", "files", "information", "stolen"],
                    weight=0.20,
                    context="Malware accessing user data"
                ),
            ],
            "extortion": [
                SignalPattern(
                    name="threat",
                    keywords=["threat", "blackmail", "expose", "publish", "leak", "threat"],
                    weight=0.30,
                    context="Explicit threats or blackmail"
                ),
                SignalPattern(
                    name="evidence_claim",
                    keywords=["evidence", "proof", "screenshot", "video", "footage", "photos"],
                    weight=0.25,
                    context="Claims to have damaging evidence"
                ),
                SignalPattern(
                    name="demand",
                    keywords=["demand", "pay", "bitcoin", "money", "payment", "ransom"],
                    weight=0.30,
                    context="Payment demand"
                ),
                SignalPattern(
                    name="urgency",
                    keywords=["hours", "immediately", "now", "soon", "deadline", "deadline"],
                    weight=0.15,
                    context="Sense of urgency"
                ),
            ],
            "ddos": [
                SignalPattern(
                    name="unavailable",
                    keywords=["down", "unavailable", "offline", "cannot access", "not working"],
                    weight=0.30,
                    context="Service is unavailable"
                ),
                SignalPattern(
                    name="traffic",
                    keywords=["traffic", "requests", "flooding", "overwhelming", "attacks"],
                    weight=0.25,
                    context="Abnormal traffic patterns"
                ),
                SignalPattern(
                    name="timing",
                    keywords=["started", "began", "since", "when", "suddenly"],
                    weight=0.20,
                    context="Timing of the attack"
                ),
                SignalPattern(
                    name="website_mention",
                    keywords=["website", "server", "service", "application", "api"],
                    weight=0.25,
                    context="Web service targeted"
                ),
            ],
            "data_breach": [
                SignalPattern(
                    name="data_exposed",
                    keywords=["data", "breach", "exposed", "leaked", "stolen", "compromised"],
                    weight=0.30,
                    context="Data confirmed exposed or stolen"
                ),
                SignalPattern(
                    name="records_count",
                    keywords=["records", "thousands", "millions", "customers", "users"],
                    weight=0.25,
                    context="Scale of breach"
                ),
                SignalPattern(
                    name="organization",
                    keywords=["company", "organization", "business", "service", "platform"],
                    weight=0.25,
                    context="Organization name"
                ),
                SignalPattern(
                    name="notification",
                    keywords=["notified", "notification", "informed", "alerted", "contacted"],
                    weight=0.20,
                    context="How victim was notified"
                ),
            ],
            "hacking": [
                SignalPattern(
                    name="unauthorized_access",
                    keywords=["hacked", "hacking", "access", "unauthorized", "compromised", "breach"],
                    weight=0.30,
                    context="Unauthorized access confirmed"
                ),
                SignalPattern(
                    name="account_takeover",
                    keywords=["account", "password", "login", "takeover", "locked", "changed"],
                    weight=0.25,
                    context="Account access compromised"
                ),
                SignalPattern(
                    name="unauthorized_action",
                    keywords=["sent", "posted", "sent", "changed", "deleted", "transferred"],
                    weight=0.25,
                    context="Unauthorized actions taken"
                ),
                SignalPattern(
                    name="discovery_method",
                    keywords=["noticed", "found", "discovered", "realized", "saw"],
                    weight=0.20,
                    context="How breach was discovered"
                ),
            ],
            "spam": [
                SignalPattern(
                    name="bulk_messages",
                    keywords=["spam", "unsolicited", "bulk", "message", "email", "sms"],
                    weight=0.25,
                    context="Bulk unsolicited messages"
                ),
                SignalPattern(
                    name="platform",
                    keywords=["email", "sms", "text", "whatsapp", "telegram", "instagram", "facebook"],
                    weight=0.20,
                    context="Platform where spam received"
                ),
                SignalPattern(
                    name="frequency",
                    keywords=["daily", "constant", "multiple", "repeatedly", "keeps"],
                    weight=0.20,
                    context="Frequency of spam"
                ),
                SignalPattern(
                    name="content_suspicious",
                    keywords=["suspicious", "phishing", "scam", "link", "click", "verify"],
                    weight=0.35,
                    context="Spam content is suspicious"
                ),
            ],
        }
    
    async def analyze_signals(self, user_input: str, target_crime_type: str = None) -> Dict:
        """
        Analyze text for crime-specific signals.
        
        Args:
            user_input: The incident description
            target_crime_type: Optional specific crime type to analyze
            
        Returns:
            Signal analysis results
        """
        user_input_lower = user_input.lower()
        
        if target_crime_type and target_crime_type in self.signal_patterns:
            # Analyze specific crime type
            patterns = self.signal_patterns[target_crime_type]
            signals_found = {}
            total_weight = 0
            
            for pattern in patterns:
                matches = sum(1 for kw in pattern.keywords if kw in user_input_lower)
                if matches > 0:
                    signals_found[pattern.name] = {
                        "matches": matches,
                        "weight": pattern.weight,
                        "context": pattern.context
                    }
                    total_weight += pattern.weight
            
            return {
                "crime_type": target_crime_type,
                "signals_found": signals_found,
                "signal_count": len(signals_found),
                "total_weight": total_weight,
                "signal_density": total_weight / len(patterns) if patterns else 0
            }
        
        else:
            # Analyze for all crime types
            all_signals = {}
            
            for crime_type, patterns in self.signal_patterns.items():
                signals_found = {}
                total_weight = 0
                
                for pattern in patterns:
                    matches = sum(1 for kw in pattern.keywords if kw in user_input_lower)
                    if matches > 0:
                        signals_found[pattern.name] = {
                            "matches": matches,
                            "weight": pattern.weight,
                        }
                        total_weight += pattern.weight
                
                all_signals[crime_type] = {
                    "signals_found": signals_found,
                    "signal_count": len(signals_found),
                    "total_weight": total_weight
                }
            
            return {
                "all_signals": all_signals,
                "analysis_type": "comprehensive"
            }
    
    def get_keyword_density(self, user_input: str, crime_type: str) -> float:
        """
        Calculate keyword density for a crime type (0-1).
        """
        if crime_type not in self.signal_patterns:
            return 0.0
        
        patterns = self.signal_patterns[crime_type]
        if not patterns:
            return 0.0
        
        user_input_lower = user_input.lower()
        total_matches = 0
        total_keywords = sum(len(p.keywords) for p in patterns)
        
        for pattern in patterns:
            total_matches += sum(1 for kw in pattern.keywords if kw in user_input_lower)
        
        return min(total_matches / total_keywords, 1.0) if total_keywords > 0 else 0.0

# Singleton instance
pattern_matcher = PatternMatcher()


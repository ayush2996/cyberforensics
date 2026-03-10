# hierarchical_classifier.py
"""
Stage Two: Hierarchical Taxonomy Classification
Breaks crime prediction into hierarchical Yes/No steps for accuracy.
"""

from llm_manager import llm
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class TaxonomyLevel:
    """Represents a level in the crime taxonomy"""
    name: str
    question: str
    branches: Dict[str, 'TaxonomyLevel'] = None

class HierarchicalTaxonomyClassifier:
    """
    Multi-level hierarchical classifier that breaks crime prediction into steps:
    Level 1: Broad Category (Financial, Personal/Harassment, Technical/Infrastructure)
    Level 2: Specific Type (e.g., Financial  Investment Fraud vs Account Takeover)
    Level 3: Sub-type (e.g., Investment Fraud  Crypto Pig-Butchering vs Pump-and-Dump)
    """
    
    def __init__(self):
        self.llm = llm
        self.taxonomy = self._build_taxonomy()
    
    def _build_taxonomy(self) -> Dict:
        """Build crime taxonomy tree"""
        return {
            "root": {
                "name": "Crime Category",
                "question": "Is this crime primarily about: A) Financial Loss, B) Personal/Harassment, or C) Technical/Infrastructure?",
                "branches": {
                    "financial": {
                        "name": "Financial Crime",
                        "question": "What type of financial crime? A) Fraud (direct money loss), B) Account Compromise (credentials/access stolen), C) Ransomware (data encrypted for payment), or D) Data Breach (information stolen)",
                        "branches": {
                            "fraud": {
                                "name": "Fraud",
                                "question": "Fraud subtype? A) Investment/Crypto Scam (Pigbutchering, pump-and-dump), B) Wire/Transfer Fraud (unauthorized transfers), or C) Merchant Fraud (fake goods/services)?",
                                "branches": {
                                    "investment_fraud": {"name": "Investment/Crypto Fraud", "crime_type": "fraud"},
                                    "wire_fraud": {"name": "Wire Fraud", "crime_type": "fraud"},
                                    "merchant_fraud": {"name": "Merchant Fraud", "crime_type": "fraud"},
                                }
                            },
                            "account_compromise": {
                                "name": "Account Compromise",
                                "question": "Is it A) Phishing (credential theft), B) Identity Theft (stolen identity used), or C) Account Takeover (access gained)?",
                                "branches": {
                                    "phishing": {"name": "Phishing", "crime_type": "phishing"},
                                    "identity_theft": {"name": "Identity Theft", "crime_type": "identity_theft"},
                                    "account_takeover": {"name": "Account Takeover", "crime_type": "hacking"},
                                }
                            },
                            "ransomware": {
                                "name": "Ransomware",
                                "question": "Ransomware context? A) Individual Computer (personal device), B) Business Systems (office/server), or C) Extortion (with data threats)?",
                                "branches": {
                                    "personal_ransomware": {"name": "Personal Ransomware", "crime_type": "ransomware"},
                                    "business_ransomware": {"name": "Business Ransomware", "crime_type": "ransomware"},
                                    "extortion_ransomware": {"name": "Extortion Ransomware", "crime_type": "extortion"},
                                }
                            },
                            "data_breach": {
                                "name": "Data Breach",
                                "question": "Breach type? A) Your data accessed (personal information stolen), B) Organization data breached (customer records), or C) Both?",
                                "branches": {
                                    "personal_breach": {"name": "Personal Data Breach", "crime_type": "identity_theft"},
                                    "organization_breach": {"name": "Organization Breach", "crime_type": "data_breach"},
                                    "combined_breach": {"name": "Combined Breach", "crime_type": "data_breach"},
                                }
                            }
                        }
                    },
                    "personal_harassment": {
                        "name": "Personal/Harassment",
                        "question": "Harassment type? A) Extortion/Threats (demanding payment/action), B) Spam (unsolicited messages), or C) Cyberbullying (harassment/abuse)?",
                        "branches": {
                            "extortion": {"name": "Extortion/Blackmail", "crime_type": "extortion"},
                            "spam": {"name": "Spam", "crime_type": "spam"},
                            "cyberbullying": {"name": "Cyberbullying", "crime_type": "spam"},  # Map to spam for now
                        }
                    },
                    "technical_infrastructure": {
                        "name": "Technical/Infrastructure",
                        "question": "Technical attack? A) Malware (malicious software), B) DDoS (service unavailable), or C) Hacking (unauthorized access)?",
                        "branches": {
                            "malware": {"name": "Malware", "crime_type": "malware"},
                            "ddos": {"name": "DDoS", "crime_type": "ddos"},
                            "hacking": {"name": "Hacking", "crime_type": "hacking"},
                        }
                    }
                }
            }
        }
    
    async def classify_hierarchical(self, user_input: str, stop_depth: int = 3) -> Dict:
        """
        Classify through taxonomy hierarchy.
        
        Args:
            user_input: Incident description
            stop_depth: How many levels deep to go (1-3)
            
        Returns:
            Classification path and final crime type
        """
        classification_path = []
        current_node = self.taxonomy["root"]
        level = 0
        
        while level < stop_depth and current_node.get("branches"):
            level += 1
            
            # Get answer for current level
            answer = await self._get_hierarchical_answer(
                user_input,
                current_node.get("question", ""),
                current_node.get("name", "")
            )
            
            classification_path.append({
                "level": level,
                "node": current_node.get("name"),
                "answer": answer
            })
            
            # Move to next level
            if answer in current_node.get("branches", {}):
                current_node = current_node["branches"][answer]
            else:
                break
        
        # Determine final crime type
        crime_type = current_node.get("crime_type", "fraud")
        
        return {
            "classification_path": classification_path,
            "final_node": current_node.get("name"),
            "crime_type": crime_type,
            "depth": level
        }
    
    async def _get_hierarchical_answer(self, user_input: str, question: str, context: str) -> str:
        """
        Get LLM to answer a hierarchical classification question.
        
        Returns the key (branch name) that best matches the user's input.
        """
        prompt = f"""
You are a cyber crime classification expert. Based on the user's incident description and the classification question, determine which category best fits.

INCIDENT DESCRIPTION:
{user_input}

CLASSIFICATION CONTEXT: {context}

QUESTION: {question}

Respond with ONLY the key (a single word like "financial", "fraud", "phishing", etc.) that best matches, no explanation.
"""
        
        system_prompt = "You are a classification expert. Respond with only a single word key, no explanation."
        
        try:
            response = self.llm.generate(prompt, system_prompt, max_tokens=50)
            answer = response.strip().lower()
            return answer
        except:
            return "fraud"  # Default fallback
    
    def visualize_path(self, classification_result: Dict) -> str:
        """
        Create a visual representation of the classification path.
        """
        lines = ["Crime Classification Path:"]
        
        path = classification_result.get("classification_path", []) if isinstance(classification_result, dict) else []
        if not path:
            return "No classification path available"
        
        for step in path:
            indent = "  " * step["level"]
            lines.append(f"{indent}Level {step['level']}: {step['node']}")
            lines.append(f"{indent}   Answer: {step['answer']}")
        
        lines.append(f"\nFinal Classification: {classification_result['crime_type']}")
        
        return "\n".join(lines)

# Singleton instance
hierarchical_classifier_instance = HierarchicalTaxonomyClassifier()
hierarchical_classifier = hierarchical_classifier_instance
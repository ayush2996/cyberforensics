from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import json

# ===================== ENUMS =====================
class CrimeType(str, Enum):
    """Supported cyber crime types"""
    PHISHING = "phishing"
    RANSOMWARE = "ransomware"
    DATA_BREACH = "data_breach"
    IDENTITY_THEFT = "identity_theft"
    FRAUD = "fraud"
    MALWARE = "malware"
    DDoS = "ddos"
    HACKING = "hacking"
    EXTORTION = "extortion"
    SPAM = "spam"

# ===================== BASE MODELS =====================
class ReportRequest(BaseModel):
    user_input: str = Field(..., min_length=10, max_length=5000)

class CrimeTypeSelectionRequest(BaseModel):
    description: str = Field(..., description="Brief description of the incident")

class CrimeTypeSelectionResponse(BaseModel):
    status: str = "success"
    detected_types: List[CrimeType]
    confidence: float
    recommendation: CrimeType
    message: str

# ===================== CRIME-SPECIFIC SCHEMAS =====================
class PhishingReport(BaseModel):
    """JSON Schema for Phishing crimes"""
    crime_type: str = CrimeType.PHISHING
    victim_email: str = Field(..., description="Email address of the victim")
    sender_email: str = Field(..., description="Email address of sender")
    email_subject: str = Field(..., description="Subject line of the email")
    email_body: str = Field(..., description="Content of the suspicious email")
    link_clicked: bool = Field(..., description="Did victim click any links?")
    suspicious_links: Optional[List[str]] = Field(default=None, description="Links in email")
    credentials_entered: bool = Field(..., description="Were credentials entered?")
    credentials_lost: Optional[List[str]] = Field(default=None, description="Type of credentials")
    date_received: datetime = Field(..., description="When was email received")
    action_taken: str = Field(..., description="What action did victim take")
    financial_loss: float = Field(default=0, description="Monetary loss in dollars")

class RansomwareReport(BaseModel):
    """JSON Schema for Ransomware attacks"""
    crime_type: str = CrimeType.RANSOMWARE
    affected_systems: List[str] = Field(..., description="Systems/devices affected")
    ransom_amount: float = Field(..., description="Ransom demand amount")
    currency: str = Field(default="USD", description="Currency of ransom")
    ransom_note: str = Field(..., description="Content of ransom message")
    file_extensions_encrypted: List[str] = Field(..., description="File types encrypted")
    date_infection: datetime = Field(..., description="When was system infected")
    ransomware_name: Optional[str] = Field(default=None, description="Type of ransomware")
    data_exfiltration: bool = Field(..., description="Was data copied before encryption?")
    backups_available: bool = Field(..., description="Are backups available?")
    backup_status: Optional[str] = Field(default=None, description="Status of backups")
    contact_made_attacker: bool = Field(..., description="Did you contact attacker?")

class DataBreachReport(BaseModel):
    """JSON Schema for Data Breaches"""
    crime_type: str = CrimeType.DATA_BREACH
    organization_name: str = Field(..., description="Name of affected organization")
    data_types: List[str] = Field(..., description="Types of data breached (PII, financial, etc)")
    records_affected: int = Field(..., description="Number of records compromised")
    discovery_date: datetime = Field(..., description="When was breach discovered")
    breach_date: Optional[datetime] = Field(default=None, description="When did breach occur")
    attack_vector: str = Field(..., description="How was data accessed (hacking, insider, etc)")
    notification_status: bool = Field(..., description="Were affected parties notified?")
    regulatory_agencies: Optional[List[str]] = Field(default=None, description="Agencies notified")
    estimated_damage: float = Field(default=0, description="Estimated financial impact")

class IdentityTheftReport(BaseModel):
    """JSON Schema for Identity Theft"""
    crime_type: str = CrimeType.IDENTITY_THEFT
    victim_name: str = Field(..., description="Full name of identity theft victim")
    victim_ssn_partial: str = Field(..., description="Last 4 digits of SSN")
    date_discovered: datetime = Field(..., description="When was theft discovered")
    fraudulent_accounts: List[str] = Field(..., description="Accounts opened fraudulently")
    credit_inquiries: int = Field(..., description="Unauthorized credit inquiries")
    financial_loss: float = Field(default=0, description="Financial loss amount")
    victim_actions: List[str] = Field(..., description="Actions taken by victim")
    credit_freeze: bool = Field(..., description="Was credit frozen?")
    fraud_alert_filed: bool = Field(..., description="Fraud alert filed with credit bureau?")

class FraudReport(BaseModel):
    """JSON Schema for Fraud cases"""
    crime_type: str = CrimeType.FRAUD
    fraud_type: str = Field(..., description="Type: wire fraud, credit card, check, etc")
    victim_name: str = Field(..., description="Name of defrauded person/company")
    amount: float = Field(..., description="Amount defrauded")
    currency: str = Field(default="USD")
    payment_method: str = Field(..., description="How was payment made")
    fraud_date: datetime = Field(..., description="When did fraud occur")
    detection_method: str = Field(..., description="How was fraud detected")
    suspect_info: Optional[str] = Field(default=None, description="Information about suspect")
    bank_name: Optional[str] = Field(default=None, description="Bank involved")
    transaction_id: Optional[str] = Field(default=None, description="Transaction reference")

class MalwareReport(BaseModel):
    """JSON Schema for Malware infections"""
    crime_type: str = CrimeType.MALWARE
    affected_systems: List[str] = Field(..., description="Systems affected")
    malware_type: str = Field(..., description="Type: trojan, worm, spyware, etc")
    detection_date: datetime = Field(..., description="When was malware detected")
    infection_date: Optional[datetime] = Field(default=None, description="Estimated infection date")
    symptoms: List[str] = Field(..., description="Observed symptoms")
    data_accessed: Optional[List[str]] = Field(default=None, description="Data potentially accessed")
    malicious_activity: str = Field(..., description="What did malware do?")
    antivirus_product: str = Field(..., description="Antivirus product used")
    quarantine_status: str = Field(..., description="Status of quarantine action")

class DDoSReport(BaseModel):
    """JSON Schema for DDoS attacks"""
    crime_type: str = CrimeType.DDoS
    target_url: str = Field(..., description="Website/service targeted")
    attack_start_time: datetime = Field(..., description="When did attack start")
    attack_duration_minutes: int = Field(..., description="How long did attack last")
    target_ip: Optional[str] = Field(default=None, description="Target IP address")
    attack_type: str = Field(..., description="Volume/Protocol/Application layer attack")
    peak_traffic: Optional[str] = Field(default=None, description="Peak traffic received")
    source_ips_count: Optional[int] = Field(default=None, description="Number of source IPs")
    downtime: int = Field(..., description="Minutes of downtime")
    financial_impact: float = Field(default=0)
    mitigation_steps: List[str] = Field(..., description="Steps taken to mitigate")

class HackingReport(BaseModel):
    """JSON Schema for Hacking/Unauthorized Access"""
    crime_type: str = CrimeType.HACKING
    entry_point: str = Field(..., description="How did attacker gain access")
    compromised_systems: List[str] = Field(..., description="Systems compromised")
    discovery_date: datetime = Field(..., description="When was hacking discovered")
    hacker_identity: Optional[str] = Field(default=None, description="Known info about hacker")
    unauthorized_actions: List[str] = Field(..., description="What did hacker do?")
    data_stolen: Optional[List[str]] = Field(default=None, description="Data exfiltrated")
    persistence_methods: Optional[List[str]] = Field(default=None, description="Backdoors installed?")
    access_duration: Optional[str] = Field(default=None, description="How long had access?")

class ExtortionReport(BaseModel):
    """JSON Schema for Extortion/Blackmail"""
    crime_type: str = CrimeType.EXTORTION
    victim_name: str = Field(..., description="Name of victim")
    extortion_method: str = Field(..., description="Email, call, social media, etc")
    threat_content: str = Field(..., description="What are they threatening?")
    demanded_amount: float = Field(..., description="Ransom/extortion amount demanded")
    currency: str = Field(default="USD")
    payment_method_requested: str = Field(..., description="How do they want payment?")
    deadline: Optional[datetime] = Field(default=None, description="Deadline for payment")
    evidence_demanded: Optional[str] = Field(default=None, description="What evidence do they claim to have?")
    contact_made: bool = Field(..., description="Did victim contact them?")
    amount_paid: float = Field(default=0, description="Amount actually paid")

class SpamReport(BaseModel):
    """JSON Schema for Spam"""
    crime_type: str = CrimeType.SPAM
    message_type: str = Field(..., description="Email, SMS, social media, etc")
    sender_address: str = Field(..., description="Sender email/phone/account")
    message_content: str = Field(..., description="Content of spam message")
    frequency: str = Field(..., description="How often received - daily, hourly, etc")
    first_received: datetime = Field(..., description="When did spam start")
    links_in_message: Optional[List[str]] = Field(default=None, description="URLs in message")
    credentials_requested: bool = Field(..., description="Did message request credentials?")
    financial_requests: bool = Field(..., description="Did message request money?")
    actions_taken: List[str] = Field(..., description="Reported/blocked, etc")

class QuestionResponse(BaseModel):
    status: str = "needs_clarification"
    questions: List[str]
    confidence: float
    crime_type: Optional[CrimeType] = None

class ReportResponse(BaseModel):
    status: str = "success"
    report_data: Dict[str, Any] = Field(..., description="Crime-specific report data in JSON")
    crime_type: CrimeType
    confidence: float
    timestamp: datetime = Field(default_factory=datetime.now)
    correlation_analysis: Optional['CorrelationResult'] = None

class CorrelationResult(BaseModel):
    """Results of correlation analysis"""
    status: str = "analyzed"  # "correlated" or "no_correlation"
    similar_cases: List[Dict[str, Any]] = Field(default_factory=list)
    matching_patterns: List[str] = Field(default_factory=list)
    matching_callers: List[str] = Field(default_factory=list)
    correlation_score: float = Field(default=0.0, ge=0, le=1)
    recommendation: str = ""
    correlated_case_ids: List[str] = Field(default_factory=list)

class HealthCheck(BaseModel):
    status: str
    apis: dict

# Update forward references
ReportResponse.model_rebuild()

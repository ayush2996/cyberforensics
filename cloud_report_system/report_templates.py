"""
Report templates for different crime types.
Each template formats the incident data according to the crime-specific format.
"""

from typing import Dict, Any, Optional


class ReportTemplate:
    """Base class for report templates."""
    
    @staticmethod
    def format_report(data: Dict[str, Any]) -> str:
        """Format report data into structured text."""
        raise NotImplementedError


class PhishingTemplate(ReportTemplate):
    """Template for phishing crime reports."""
    
    @staticmethod
    def format_report(data: Dict[str, Any]) -> str:
        return f"""
═══════════════════════════════════════════════════════════════════════════════
                           PHISHING COMPLAINT REPORT
═══════════════════════════════════════════════════════════════════════════════

To,
The Station House Officer (SHO) / In-Charge,
Cyber Crime Police Station

Subject: Complaint regarding Phishing Attack and Unauthorized Access of Credentials

Respected Sir/Madam,

═══════════════════════════════════════════════════════════════════════════════
1) INCIDENT SUMMARY (CHRONOLOGY)
═══════════════════════════════════════════════════════════════════════════════

Date Received: {data.get('date_received', 'Not provided')}
Email Subject: {data.get('email_subject', 'Not provided')}

Description of Events:
On {data.get('date_received', 'the date mentioned')}, I received a phishing email from 
"{data.get('sender_email', 'unknown sender')}" with subject "{data.get('email_subject', 'N/A')}".

The email contained a suspicious link: {data.get('link_clicked', 'Not disclosed')}

Link Clicked: {data.get('link_clicked', 'No') if data.get('link_clicked') else 'No'}

═══════════════════════════════════════════════════════════════════════════════
2) CREDENTIAL EXPOSURE DETAILS
═══════════════════════════════════════════════════════════════════════════════

Victim Email Address: {data.get('victim_email', 'Not provided')}
Credentials Entered: {data.get('credentials_entered', 'Unknown')}
Credentials Lost/Compromised: {data.get('credentials_lost', 'Unknown')}

═══════════════════════════════════════════════════════════════════════════════
3) FINANCIAL IMPACT
═══════════════════════════════════════════════════════════════════════════════

Reported Financial Loss: ₹ {data.get('financial_loss', '0')}

═══════════════════════════════════════════════════════════════════════════════
4) ACTION TAKEN BY COMPLAINANT
═══════════════════════════════════════════════════════════════════════════════

Actions Taken: {data.get('action_taken', 'None specified')}

═══════════════════════════════════════════════════════════════════════════════
5) REQUEST
═══════════════════════════════════════════════════════════════════════════════

I request you to kindly:
• Register this complaint for phishing and unauthorized credential access
• Investigate the fraudulent email address: {data.get('sender_email', 'N/A')}
• Trace the malicious link and take action against the perpetrators
• Facilitate recovery of any unauthorized transactions if applicable
• Advise on protective measures

I declare that the above information is true to the best of my knowledge.

Report Generated: {data.get('report_date', 'N/A')}
Case ID: {data.get('case_id', 'N/A')}

═══════════════════════════════════════════════════════════════════════════════
"""


class FraudTemplate(ReportTemplate):
    """Template for online fraud/financial fraud reports."""
    
    @staticmethod
    def format_report(data: Dict[str, Any]) -> str:
        return f"""
═══════════════════════════════════════════════════════════════════════════════
                      ONLINE FINANCIAL FRAUD COMPLAINT REPORT
═══════════════════════════════════════════════════════════════════════════════

To,
The Station House Officer (SHO) / In-Charge,
Cyber Crime Police Station

Subject: Complaint regarding Online Financial Fraud of ₹{data.get('amount', '______')} on {data.get('fraud_date', '__/__/____')}

Respected Sir/Madam,

═══════════════════════════════════════════════════════════════════════════════
1) COMPLAINANT DETAILS
═══════════════════════════════════════════════════════════════════════════════

Name: {data.get('victim_name', '_______________________________')}
Contact Details: Available on file

═══════════════════════════════════════════════════════════════════════════════
2) INCIDENT SUMMARY (CHRONOLOGY)
═══════════════════════════════════════════════════════════════════════════════

Date of Fraud: {data.get('fraud_date', '__/__/____')}
Type of Fraud: {data.get('fraud_type', '_____________________________')}

Description:
{data.get('suspect_info', 'Fraudster engaged through deceptive means')}

Method of Detection: {data.get('detection_method', 'Unauthorized transaction detected')}

═══════════════════════════════════════════════════════════════════════════════
3) TRANSACTION DETAILS
═══════════════════════════════════════════════════════════════════════════════

Bank/Financial Provider: {data.get('bank_name', '______________________')}
Payment Method: {data.get('payment_method', '_____________________')}
Amount Defrauded: ₹{data.get('amount', '___________________________')}
Transaction ID / UTR / RRN: {data.get('transaction_id', '__________')}

═══════════════════════════════════════════════════════════════════════════════
4) SUSPECT DETAILS (IF KNOWN)
═══════════════════════════════════════════════════════════════════════════════

Suspect Information: {data.get('suspect_info', '____________________')}

═══════════════════════════════════════════════════════════════════════════════
5) ACTION ALREADY TAKEN
═══════════════════════════════════════════════════════════════════════════════

• Bank/Financial Institution Contacted: Yes
• Account/Transaction Blocked: Yes (if applicable)
• FIR/Police Complaint Initiated: In Progress

═══════════════════════════════════════════════════════════════════════════════
6) REQUEST
═══════════════════════════════════════════════════════════════════════════════

I request you to kindly register my complaint and take necessary action to:
• Investigate the matter thoroughly
• Identify and apprehend the fraudsters
• Recover the amount of ₹{data.get('amount', '0')} if possible
• Take preventive measures against such frauds

I declare that the above information is true to the best of my knowledge.

Report Generated: {data.get('report_date', 'N/A')}
Case ID: {data.get('case_id', 'N/A')}

═══════════════════════════════════════════════════════════════════════════════
"""


class RansomwareTemplate(ReportTemplate):
    """Template for ransomware attack reports."""
    
    @staticmethod
    def format_report(data: Dict[str, Any]) -> str:
        return f"""
═══════════════════════════════════════════════════════════════════════════════
                          RANSOMWARE ATTACK COMPLAINT REPORT
═══════════════════════════════════════════════════════════════════════════════

To,
The Station House Officer (SHO) / In-Charge,
Cyber Crime Police Station

Subject: Complaint regarding Ransomware Attack and Extortion Threat

Respected Sir/Madam,

═══════════════════════════════════════════════════════════════════════════════
1) INCIDENT SUMMARY
═══════════════════════════════════════════════════════════════════════════════

Date of Infection: {data.get('date_infection', '__/__/____')}
Ransomware Name: {data.get('ransomware_name', 'Unknown')}

Description:
My system(s) was/were infected with ransomware on {data.get('date_infection', 'the date mentioned')}.
The ransomware encrypted my files with extensions: {data.get('file_extensions_encrypted', 'Various')}

═══════════════════════════════════════════════════════════════════════════════
2) AFFECTED SYSTEMS & DATA
═══════════════════════════════════════════════════════════════════════════════

Affected Systems: {data.get('affected_systems', '_____________________________')}
Data Exfiltration: {data.get('data_exfiltration', 'Unknown')}
Backups Available: {data.get('backups_available', 'Unknown')}

═══════════════════════════════════════════════════════════════════════════════
3) RANSOM DEMAND
═══════════════════════════════════════════════════════════════════════════════

Ransom Amount Demanded: {data.get('currency', 'Please confirm currency')} {data.get('ransom_amount', '______')}
Ransom Note/Instructions: 
{data.get('ransom_note', 'Contact made by attacker (details below)')}

═══════════════════════════════════════════════════════════════════════════════
4) EXTORTION ATTEMPT
═══════════════════════════════════════════════════════════════════════════════

Contact Made with Attacker: {data.get('contact_made_attacker', 'No')}
Payment Status: {'Paid' if data.get('contact_made_attacker') == 'Yes' else 'No payment made'}

═══════════════════════════════════════════════════════════════════════════════
5) REQUEST
═══════════════════════════════════════════════════════════════════════════════

I request you to kindly:
• Register this complaint for ransomware infection and extortion
• Investigate the attack and identify the threat actors
• Issue advisories to prevent similar incidents
• Facilitate decryption solutions if available
• Take action against the perpetrators

I declare that the above information is true to the best of my knowledge.

Report Generated: {data.get('report_date', 'N/A')}
Case ID: {data.get('case_id', 'N/A')}

═══════════════════════════════════════════════════════════════════════════════
"""


class DataBreachTemplate(ReportTemplate):
    """Template for data breach reports."""
    
    @staticmethod
    def format_report(data: Dict[str, Any]) -> str:
        return f"""
═══════════════════════════════════════════════════════════════════════════════
                              DATA BREACH COMPLAINT REPORT
═══════════════════════════════════════════════════════════════════════════════

To,
The Station House Officer (SHO) / In-Charge,
Cyber Crime Police Station

Subject: Complaint regarding Unauthorized Data Breach and Information Exposure

Respected Sir/Madam,

═══════════════════════════════════════════════════════════════════════════════
1) ORGANIZATION & BREACH SUMMARY
═══════════════════════════════════════════════════════════════════════════════

Organization Name: {data.get('organization_name', '_____________________________')}
Discovery Date: {data.get('discovery_date', '__/__/____')}

Description:
My personal data was compromised in an unauthorized data breach affecting the above organization.

═══════════════════════════════════════════════════════════════════════════════
2) DATA COMPROMISED
═══════════════════════════════════════════════════════════════════════════════

Types of Data Exposed: {data.get('data_types', 'Personal Information')}
Number of Records Affected: {data.get('records_affected', 'Multiple')}
Attack Vector: {data.get('attack_vector', 'Unknown')}
Estimated Damage: {data.get('estimated_damage', 'Significant')}

═══════════════════════════════════════════════════════════════════════════════
3) NOTIFICATION STATUS
═══════════════════════════════════════════════════════════════════════════════

Notification Received: {data.get('notification_status', 'No')}
Date of Notification: {data.get('discovery_date', 'N/A')}

═══════════════════════════════════════════════════════════════════════════════
4) REQUEST
═══════════════════════════════════════════════════════════════════════════════

I request you to kindly:
• Register this data breach complaint
• Investigate the breach and identify the responsible parties
• Issue notices to the affected organization
• Take preventive measures and enforce data protection compliance
• Advise on identity theft protection measures

I declare that the above information is true to the best of my knowledge.

Report Generated: {data.get('report_date', 'N/A')}
Case ID: {data.get('case_id', 'N/A')}

═══════════════════════════════════════════════════════════════════════════════
"""


class IdentityTheftTemplate(ReportTemplate):
    """Template for identity theft reports."""
    
    @staticmethod
    def format_report(data: Dict[str, Any]) -> str:
        return f"""
═══════════════════════════════════════════════════════════════════════════════
                            IDENTITY THEFT COMPLAINT REPORT
═══════════════════════════════════════════════════════════════════════════════

To,
The Station House Officer (SHO) / In-Charge,
Cyber Crime Police Station

Subject: Complaint regarding Identity Theft and Fraudulent Accounts

Respected Sir/Madam,

═══════════════════════════════════════════════════════════════════════════════
1) VICTIM DETAILS
═══════════════════════════════════════════════════════════════════════════════

Name: {data.get('victim_name', '_______________________________')}
Date Discovered: {data.get('date_discovered', '__/__/____')}

═══════════════════════════════════════════════════════════════════════════════
2) IDENTITY THEFT SUMMARY
═══════════════════════════════════════════════════════════════════════════════

Fraudulent Accounts Created: {data.get('fraudulent_accounts', 'Multiple accounts')}
Credit Inquiries Made: {data.get('credit_inquiries', 'Multiple')}
Financial Loss: ₹ {data.get('financial_loss', '0')}

═══════════════════════════════════════════════════════════════════════════════
3) PROTECTIVE MEASURES TAKEN
═══════════════════════════════════════════════════════════════════════════════

Credit Freeze: {data.get('credit_freeze', 'No')}
Fraud Alert Filed: {data.get('fraud_alert_filed', 'No')}

═══════════════════════════════════════════════════════════════════════════════
4) REQUEST
═══════════════════════════════════════════════════════════════════════════════

I request you to kindly:
• Register this identity theft complaint
• Investigate the unauthorized use of my identity
• Take action against the perpetrators
• Help in closing fraudulent accounts
• Advise on credit monitoring and protection

I declare that the above information is true to the best of my knowledge.

Report Generated: {data.get('report_date', 'N/A')}
Case ID: {data.get('case_id', 'N/A')}

═══════════════════════════════════════════════════════════════════════════════
"""


class MalwareTemplate(ReportTemplate):
    """Template for malware infection reports."""
    
    @staticmethod
    def format_report(data: Dict[str, Any]) -> str:
        return f"""
═══════════════════════════════════════════════════════════════════════════════
                            MALWARE INFECTION COMPLAINT REPORT
═══════════════════════════════════════════════════════════════════════════════

To,
The Station House Officer (SHO) / In-Charge,
Cyber Crime Police Station

Subject: Complaint regarding Malware Infection and Unauthorized Data Access

Respected Sir/Madam,

═══════════════════════════════════════════════════════════════════════════════
1) INCIDENT SUMMARY
═══════════════════════════════════════════════════════════════════════════════

Detection Date: {data.get('detection_date', '__/__/____')}
Malware Type: {data.get('malware_type', 'Unknown')}

Description:
My system(s) was/were infected with malware that resulted in unauthorized access to personal data.

═══════════════════════════════════════════════════════════════════════════════
2) AFFECTED SYSTEMS & DATA
═══════════════════════════════════════════════════════════════════════════════

Affected Systems: {data.get('affected_systems', '_____________________________')}
Symptoms Observed: {data.get('symptoms', 'Suspicious activity')}
Data Accessed: {data.get('data_accessed', 'Personal information')}
Malicious Activity: {data.get('malicious_activity', 'Data exfiltration attempted')}

═══════════════════════════════════════════════════════════════════════════════
3) REMEDIATION STATUS
═══════════════════════════════════════════════════════════════════════════════

Antivirus Product Used: {data.get('antivirus_product', '_______________________')}
Quarantine Status: {data.get('quarantine_status', 'Pending confirmation')}

═══════════════════════════════════════════════════════════════════════════════
4) REQUEST
═══════════════════════════════════════════════════════════════════════════════

I request you to kindly:
• Register this malware infection complaint
• Investigate the source of malware distribution
• Take action against malware developers/distributors
• Issue security advisories
• Advise on system hardening and protection

I declare that the above information is true to the best of my knowledge.

Report Generated: {data.get('report_date', 'N/A')}
Case ID: {data.get('case_id', 'N/A')}

═══════════════════════════════════════════════════════════════════════════════
"""


class DDoSTemplate(ReportTemplate):
    """Template for DDoS attack reports."""
    
    @staticmethod
    def format_report(data: Dict[str, Any]) -> str:
        return f"""
═══════════════════════════════════════════════════════════════════════════════
                          DDoS ATTACK COMPLAINT REPORT
═══════════════════════════════════════════════════════════════════════════════

To,
The Station House Officer (SHO) / In-Charge,
Cyber Crime Police Station

Subject: Complaint regarding Distributed Denial of Service (DDoS) Attack

Respected Sir/Madam,

═══════════════════════════════════════════════════════════════════════════════
1) VICTIM DETAILS
═══════════════════════════════════════════════════════════════════════════════

Target URL: {data.get('target_url', '_____________________________')}
Attack Start Time: {data.get('attack_start_time', '__/__/____ __:__')}
Attack Duration: {data.get('attack_duration_minutes', '______')} minutes

═══════════════════════════════════════════════════════════════════════════════
2) ATTACK DETAILS
═══════════════════════════════════════════════════════════════════════════════

Type of Attack: {data.get('attack_type', 'DDoS')}
Peak Traffic: {data.get('peak_traffic', 'Significant')}
Downtime Caused: {data.get('downtime', 'Substantial service disruption')}

═══════════════════════════════════════════════════════════════════════════════
3) IMPACT & MITIGATION
═══════════════════════════════════════════════════════════════════════════════

Financial Impact: {data.get('financial_impact', 'To be assessed')}
Mitigation Steps Taken: {data.get('mitigation_steps', 'Server migration and filtering')}

═══════════════════════════════════════════════════════════════════════════════
4) REQUEST
═══════════════════════════════════════════════════════════════════════════════

I request you to kindly:
• Register this DDoS attack complaint
• Investigate the source of the attack
• Take action against the perpetrators
• Coordinate with service providers for attack mitigation
• Issue advisories to prevent similar attacks

I declare that the above information is true to the best of my knowledge.

Report Generated: {data.get('report_date', 'N/A')}
Case ID: {data.get('case_id', 'N/A')}

═══════════════════════════════════════════════════════════════════════════════
"""


class HackingTemplate(ReportTemplate):
    """Template for hacking/unauthorized access reports."""
    
    @staticmethod
    def format_report(data: Dict[str, Any]) -> str:
        return f"""
═══════════════════════════════════════════════════════════════════════════════
                    UNAUTHORIZED HACKING ACCESS COMPLAINT REPORT
═══════════════════════════════════════════════════════════════════════════════

To,
The Station House Officer (SHO) / In-Charge,
Cyber Crime Police Station

Subject: Complaint regarding Unauthorized Access and Hacking of System/Account

Respected Sir/Madam,

═══════════════════════════════════════════════════════════════════════════════
1) INCIDENT SUMMARY
═══════════════════════════════════════════════════════════════════════════════

Discovery Date: {data.get('discovery_date', '__/__/____')}
Entry Point: {data.get('entry_point', 'Unknown')}

Description:
My system/account was compromised by an unauthorized third party through hacking.

═══════════════════════════════════════════════════════════════════════════════
2) COMPROMISE DETAILS
═══════════════════════════════════════════════════════════════════════════════

Compromised Systems: {data.get('compromised_systems', '_______________________')}
Duration of Access: {data.get('access_duration', 'Unknown')}
Persistence Methods: {data.get('persistence_methods', 'Possible backdoor installation')}

═══════════════════════════════════════════════════════════════════════════════
3) IMPACT ON DATA & SERVICES
═══════════════════════════════════════════════════════════════════════════════

Unauthorized Actions Performed: {data.get('unauthorized_actions', 'Data access/modification')}
Data Stolen: {data.get('data_stolen', 'Amount unknown')}

═══════════════════════════════════════════════════════════════════════════════
4) REQUEST
═══════════════════════════════════════════════════════════════════════════════

I request you to kindly:
• Register this unauthorized hacking complaint
• Investigate the source of the breach
• Identify the hacker(s)
• Help in securing the compromised systems
• Take preventive measures

I declare that the above information is true to the best of my knowledge.

Report Generated: {data.get('report_date', 'N/A')}
Case ID: {data.get('case_id', 'N/A')}

═══════════════════════════════════════════════════════════════════════════════
"""


class ExtortionTemplate(ReportTemplate):
    """Template for cyber extortion/blackmail reports."""
    
    @staticmethod
    def format_report(data: Dict[str, Any]) -> str:
        return f"""
═══════════════════════════════════════════════════════════════════════════════
                        CYBER EXTORTION COMPLAINT REPORT
═══════════════════════════════════════════════════════════════════════════════

To,
The Station House Officer (SHO) / In-Charge,
Cyber Crime Police Station

Subject: Complaint regarding Cyber Extortion and Blackmail Threat

Respected Sir/Madam,

═══════════════════════════════════════════════════════════════════════════════
1) EXTORTION SUMMARY
═══════════════════════════════════════════════════════════════════════════════

Method of Extortion: {data.get('extortion_method', 'Unknown')}
Demanded Amount: {data.get('demanded_amount', '_____________________________')}
Demanded Payment Method: {data.get('payment_method_requested', 'Cryptocurrency/Bank Transfer')}
Deadline: {data.get('deadline', 'Unspecified')}

═══════════════════════════════════════════════════════════════════════════════
2) THREAT DETAILS
═══════════════════════════════════════════════════════════════════════════════

Threat Content:
{data.get('threat_content', 'Extortionist threatened to publicize private information')}

Evidence Claimed: {data.get('evidence_claimed', 'Personal/private data')}

═══════════════════════════════════════════════════════════════════════════════
3) EXTORTIONIST CONTACT & PAYMENT STATUS
═══════════════════════════════════════════════════════════════════════════════

Contact Made: {data.get('contact_made', 'Yes')}
Amount Paid: {data.get('amount_paid', '₹ 0 (No payment made)')}

═══════════════════════════════════════════════════════════════════════════════
4) REQUEST
═══════════════════════════════════════════════════════════════════════════════

I request you to kindly:
• Register this cyber extortion and blackmail complaint
• Investigate and trace the extortionist
• Take action against the perpetrators
• Recover any amounts paid if applicable
• Provide protection and security advisories

I declare that the above information is true to the best of my knowledge.

Report Generated: {data.get('report_date', 'N/A')}
Case ID: {data.get('case_id', 'N/A')}

═══════════════════════════════════════════════════════════════════════════════
"""


class SpamTemplate(ReportTemplate):
    """Template for spam/harassment reports."""
    
    @staticmethod
    def format_report(data: Dict[str, Any]) -> str:
        return f"""
═══════════════════════════════════════════════════════════════════════════════
                            SPAM COMPLAINT REPORT
═══════════════════════════════════════════════════════════════════════════════

To,
The Station House Officer (SHO) / In-Charge,
Cyber Crime Police Station

Subject: Complaint regarding Spam Messages and Online Harassment

Respected Sir/Madam,

═══════════════════════════════════════════════════════════════════════════════
1) SPAM SUMMARY
═══════════════════════════════════════════════════════════════════════════════

Type of Message: {data.get('message_type', 'Email/SMS/WhatsApp')}
Sender Address: {data.get('sender_address', '_______________________')}
First Received: {data.get('first_received', '__/__/____')}
Frequency: {data.get('frequency', 'Multiple messages')}

═══════════════════════════════════════════════════════════════════════════════
2) MESSAGE CONTENT
═══════════════════════════════════════════════════════════════════════════════

Message Content:
{data.get('message_content', 'Unsolicited promotional/malicious content')}

═══════════════════════════════════════════════════════════════════════════════
3) FRAUDULENT REQUESTS
═══════════════════════════════════════════════════════════════════════════════

Credentials Requested: {data.get('credentials_requested', 'No')}
Financial Requests Made: {data.get('financial_requests', 'No')}
Actions Taken by Recipient: {data.get('actions_taken', 'No action/reported')}

═══════════════════════════════════════════════════════════════════════════════
4) REQUEST
═══════════════════════════════════════════════════════════════════════════════

I request you to kindly:
• Register this spam and harassment complaint
• Investigate and identify the spammer(s)
• Block the sender accounts
• Take action against the perpetrators
• Issue advisories to prevent similar spam

I declare that the above information is true to the best of my knowledge.

Report Generated: {data.get('report_date', 'N/A')}
Case ID: {data.get('case_id', 'N/A')}

═══════════════════════════════════════════════════════════════════════════════
"""


# ── Template Mapping ──────────────────────────────────────────────────────────

TEMPLATE_MAPPING = {
    "phishing": PhishingTemplate,
    "ransomware": RansomwareTemplate,
    "data_breach": DataBreachTemplate,
    "identity_theft": IdentityTheftTemplate,
    "fraud": FraudTemplate,
    "malware": MalwareTemplate,
    "ddos": DDoSTemplate,
    "hacking": HackingTemplate,
    "extortion": ExtortionTemplate,
    "spam": SpamTemplate,
}


def generate_formatted_report(crime_type: str, data: Dict[str, Any]) -> str:
    """
    Generate a formatted report based on crime type.
    
    Args:
        crime_type: Type of crime (must be in TEMPLATE_MAPPING)
        data: Dictionary of report data with field values
    
    Returns:
        Formatted report as a string
    """
    template_class = TEMPLATE_MAPPING.get(crime_type.lower())
    
    if not template_class:
        # Fallback to generic format if crime type not found
        return _generate_generic_report(data)
    
    return template_class.format_report(data)


def _generate_generic_report(data: Dict[str, Any]) -> str:
    """Generate a generic report format."""
    return f"""
═══════════════════════════════════════════════════════════════════════════════
                            CYBERCRIME COMPLAINT REPORT
═══════════════════════════════════════════════════════════════════════════════

Case ID: {data.get('case_id', 'N/A')}
Report Generated: {data.get('report_date', 'N/A')}

INCIDENT DETAILS:

{format_dict_as_text(data)}

═══════════════════════════════════════════════════════════════════════════════

I declare that the above information is true to the best of my knowledge.

═══════════════════════════════════════════════════════════════════════════════
"""


def format_dict_as_text(data: Dict[str, Any], indent: int = 0) -> str:
    """Format a dictionary as readable text."""
    lines = []
    for key, value in data.items():
        if value is None or value == "":
            continue
        formatted_key = key.replace('_', ' ').title()
        lines.append(f"{'  ' * indent}{formatted_key}: {value}")
    return "\n".join(lines)

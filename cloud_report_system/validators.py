"""
Field validators for cybercrime reporting.
Validates email, phone, dates, amounts, URLs, and other field types.
"""

import re
from datetime import datetime
from typing import Tuple, Optional


class FieldValidator:
    """Validates extracted fields for crime reports."""
    
    # Field patterns and validation rules
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE_PATTERN = r'^[\d\s\-\+\(\)]{10,}$'  # At least 10 digits
    URL_PATTERN = r'^https?://[^\s]+'
    CURRENCY_PATTERN = r'^\d+(\.\d{2})?$'
    
    # Field type mappings
    FIELD_TYPES = {
        # Email fields
        'victim_email': 'email',
        'sender_email': 'email',
        'fraudulent_email': 'email',
        'email_subject': 'text',
        
        # URL fields
        'link_clicked': 'url',
        'target_url': 'url',
        
        # Phone fields
        'victim_phone': 'phone',
        'attacker_phone': 'phone',
        'suspect_phone': 'phone',
        'contact_number': 'phone',
        
        # Date fields
        'date_received': 'date',
        'discovery_date': 'date',
        'date_discovered': 'date',
        'date_infection': 'date',
        'fraud_date': 'date',
        'detection_date': 'date',
        'attack_start_time': 'datetime',
        'attack_date': 'date',
        
        # Amount/Financial fields
        'financial_loss': 'amount',
        'ransom_amount': 'amount',
        'amount': 'amount',
        'payment_amount': 'amount',
        'amount_paid': 'amount',
        'demanded_amount': 'amount',
        'estimated_damage': 'amount',
        'peak_traffic': 'text',  # Usually in Mbps/Gbps
        'financial_impact': 'amount',
        'transaction_id': 'text',
        
        # Numeric fields
        'records_affected': 'number',
        'attack_duration_minutes': 'number',
        'credit_inquiries': 'number',
        'frequency': 'number',
        
        # Boolean/Yes-No fields
        'credentials_lost': 'boolean',
        'data_exfiltration': 'boolean',
        'backups_available': 'boolean',
        'notification_status': 'boolean',
        'credit_freeze': 'boolean',
        'fraud_alert_filed': 'boolean',
        'contact_made_attacker': 'boolean',
        'contact_made': 'boolean',
        'downtime': 'boolean',
        'credentials_requested': 'boolean',
        'financial_requests': 'boolean',
        
        # Text fields (flexible)
        'victim_name': 'text',
        'organization_name': 'text',
        'bank_name': 'text',
        'malware_name': 'ransomware_name',
        'ransomware_name': 'text',
        'fraud_type': 'text',
        'malware_type': 'text',
        'attack_type': 'text',
        'entry_point': 'text',
        'symptoms': 'text',
        'data_types': 'text',
        'email_content': 'text',
        'message_content': 'text',
        'ransom_note': 'text',
        'data_stolen': 'text',
        'threat_content': 'text',
        'evidence_claimed': 'text',
    }
    
    @classmethod
    def get_field_type(cls, field_name: str) -> str:
        """Get the validation type for a field."""
        return cls.FIELD_TYPES.get(field_name, 'text')
    
    @classmethod
    def validate_field(cls, field_name: str, value: any) -> Tuple[bool, Optional[str]]:
        """
        Validate a field value.
        Returns: (is_valid, error_message)
        """
        if value is None or value == "":
            return False, "Value cannot be empty"
        
        value_str = str(value).strip()
        
        # Single character is never valid (like "ayush" for email)
        if len(value_str) < 2:
            return False, "Value too short"
        
        field_type = cls.get_field_type(field_name)
        
        if field_type == 'email':
            return cls._validate_email(value_str)
        elif field_type == 'phone':
            return cls._validate_phone(value_str)
        elif field_type == 'url':
            return cls._validate_url(value_str)
        elif field_type == 'date':
            return cls._validate_date(value_str)
        elif field_type == 'datetime':
            return cls._validate_datetime(value_str)
        elif field_type == 'amount':
            return cls._validate_amount(value_str)
        elif field_type == 'number':
            return cls._validate_number(value_str)
        elif field_type == 'boolean':
            return cls._validate_boolean(value_str)
        else:  # text
            return cls._validate_text(value_str)
    
    @classmethod
    def _validate_email(cls, value: str) -> Tuple[bool, Optional[str]]:
        """Validate email address."""
        if not re.match(cls.EMAIL_PATTERN, value):
            return False, f"Invalid email format: '{value}'. Please enter a valid email (e.g., example@domain.com)"
        return True, None
    
    @classmethod
    def _validate_phone(cls, value: str) -> Tuple[bool, Optional[str]]:
        """Validate phone number."""
        # Remove common separators
        clean = value.replace('-', '').replace(' ', '').replace('(', '').replace(')', '').replace('+', '')
        if not clean.isdigit() or len(clean) < 10:
            return False, f"Invalid phone number: '{value}'. Please enter a valid phone with at least 10 digits"
        return True, None
    
    @classmethod
    def _validate_url(cls, value: str) -> Tuple[bool, Optional[str]]:
        """Validate URL."""
        if not re.match(cls.URL_PATTERN, value):
            return False, f"Invalid URL: '{value}'. Please enter a valid URL starting with http:// or https://"
        return True, None
    
    @classmethod
    def _validate_date(cls, value: str) -> Tuple[bool, Optional[str]]:
        """Validate date in common formats."""
        date_formats = [
            '%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y',
            '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y',
            '%d %b %Y', '%d %B %Y',
            '%B %d, %Y', '%b %d, %Y',
            '%d %b', '%d %B',
        ]
        
        for fmt in date_formats:
            try:
                datetime.strptime(value, fmt)
                return True, None
            except ValueError:
                continue
        
        return False, f"Invalid date: '{value}'. Please use formats like YYYY-MM-DD, DD/MM/YYYY, or '15 Jan 2024'"
    
    @classmethod
    def _validate_datetime(cls, value: str) -> Tuple[bool, Optional[str]]:
        """Validate datetime."""
        datetime_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%d-%m-%Y %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%d-%m-%Y %H:%M',
        ]
        
        for fmt in datetime_formats:
            try:
                datetime.strptime(value, fmt)
                return True, None
            except ValueError:
                continue
        
        return False, f"Invalid datetime: '{value}'. Please use format like YYYY-MM-DD HH:MM:SS"
    
    @classmethod
    def _validate_amount(cls, value: str) -> Tuple[bool, Optional[str]]:
        """Validate financial amount."""
        # Remove common currency symbols
        clean = value.replace('$', '').replace('€', '').replace('₹', '').replace('£', '').strip()
        clean = clean.replace(',', '')  # Remove thousand separators
        
        try:
            amount = float(clean)
            # Check if it's a reasonable amount (not 0 and not negative)
            if amount < 0:
                return False, f"Amount cannot be negative: '{value}'"
            if amount == 0:
                return False, f"Amount cannot be zero"
            if amount > 999999999:  # Sanity check for extremely large amounts
                return False, f"Amount seems unreasonably large: '{value}'. Please verify"
            return True, None
        except ValueError:
            return False, f"Invalid amount: '{value}'. Please enter a number (e.g., 45000 or 45,000)"
    
    @classmethod
    def _validate_number(cls, value: str) -> Tuple[bool, Optional[str]]:
        """Validate integer number."""
        try:
            num = int(value.replace(',', ''))
            if num < 0:
                return False, f"Cannot be negative: '{value}'"
            return True, None
        except ValueError:
            return False, f"Invalid number: '{value}'. Please enter a whole number"
    
    @classmethod
    def _validate_boolean(cls, value: str) -> Tuple[bool, Optional[str]]:
        """Validate boolean (yes/no) value."""
        valid_values = ['yes', 'no', 'true', 'false', 'y', 'n', '1', '0', 'true', 'false']
        if value.lower() not in valid_values:
            return False, f"Please answer 'yes' or 'no' — you said '{value}'"
        return True, None
    
    @classmethod
    def _validate_text(cls, value: str) -> Tuple[bool, Optional[str]]:
        """Validate generic text field."""
        if len(value) < 2:
            return False, "Response too short. Please provide more detail"
        if len(value) > 5000:
            return False, "Response too long. Please keep it under 5000 characters"
        return True, None
    
    @classmethod
    def get_validation_instruction(cls, field_name: str) -> str:
        """Get a helpful validation instruction for the LLM."""
        field_type = cls.get_field_type(field_name)
        
        instructions = {
            'email': "Must be a valid email format (e.g., user@domain.com)",
            'phone': "Must have at least 10 digits (with optional separators)",
            'url': "Must start with http:// or https://",
            'date': "Valid date formats: YYYY-MM-DD, DD/MM/YYYY, or '15 Jan 2024'",
            'datetime': "Valid format: YYYY-MM-DD HH:MM:SS",
            'amount': "Numeric amount, can include currency symbol (e.g., 45000 or $45,000)",
            'number': "Must be a whole number",
            'boolean': "Must be 'yes' or 'no'",
            'text': "Free text, minimum 2 characters",
        }
        
        return instructions.get(field_type, "Valid text response")

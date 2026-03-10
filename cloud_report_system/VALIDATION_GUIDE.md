# Field Validation System

This guide explains how the new field validation system works in the ARIA chatbot.

## Overview

The validation system ensures that extracted information is in the correct format before being saved to the report. If a user provides invalid information (like an invalid email or phone number), the system will:

1. **Reject the invalid input** — It will NOT be stored in the report
2. **Ask again** — The LLM will ask the user to provide the correct format
3. **Provide feedback** — Show the user what's wrong and what format is expected

## Supported Field Types

### Email Fields
- `victim_email`
- `sender_email`
- `fraudulent_email`
- **Format**: `user@domain.com`
- **Example**: Invalid: "ayush" → Valid: "ayush@example.com"

### Phone Fields
- `victim_phone`
- `attacker_phone`
- `suspect_phone`
- `contact_number`
- **Format**: At least 10 digits (separators optional)
- **Example**: Invalid: "123" → Valid: "+1-234-567-8900" or "9876543210"

### URL Fields
- `link_clicked`
- `target_url`
- **Format**: Must start with `http://` or `https://`
- **Example**: Invalid: "example.com" → Valid: "https://example.com"

### Date Fields
- `date_received`
- `discovery_date`
- `date_discovered`
- `date_infection`
- `fraud_date`
- `detection_date`
- `attack_date`
- **Formats Supported**:
  - `YYYY-MM-DD` (2024-01-15)
  - `DD/MM/YYYY` (15/01/2024)
  - `DD Month YYYY` (15 Jan 2024)
  - `Month DD, YYYY` (January 15, 2024)

### Datetime Fields
- `attack_start_time`
- **Format**: `YYYY-MM-DD HH:MM:SS`
- **Example**: "2024-01-15 14:30:00"

### Amount/Financial Fields
- `financial_loss`
- `ransom_amount`
- `amount`
- `amount_paid`
- `payment_amount`
- `demanded_amount`
- `estimated_damage`
- `financial_impact`
- **Format**: Numeric value (currency symbols optional)
- **Example**: Invalid: "lots" → Valid: "50000" or "$50,000" or "₹50,000"

### Numeric Fields
- `records_affected`
- `attack_duration_minutes`
- `credit_inquiries`
- `frequency`
- **Format**: Whole number (no decimals)
- **Example**: Invalid: "around 100" → Valid: "100"

### Boolean Fields (Yes/No)
- `credentials_lost`
- `data_exfiltration`
- `backups_available`
- `notification_status`
- `credit_freeze`
- `fraud_alert_filed`
- `contact_made_attacker`
- `contact_made`
- `downtime`
- `credentials_requested`
- `financial_requests`
- **Format**: "yes" or "no"
- **Example**: Invalid: "maybe" → Valid: "yes"

### Text Fields
- All other fields
- **Requirements**: Minimum 2 characters, maximum 5000 characters
- **Example**: Invalid: "a" → Valid: "The attacker sent a phishing email"

## How It Works

### Example Conversation

**User**: "My email is ayush"  
**ARIA**: (Extracts: victim_email = "ayush")  
(Validation fails: "Invalid email format")  
(Field not stored, validation error tracked)

**ARIA** (next message): "I noticed the email format might not be complete. Could you provide your full email address including the domain? For example: yourname@domain.com"

**User**: "ayush@gmail.com"  
**ARIA**: (Extracts: victim_email = "ayush@gmail.com")  
(Validation passes: Valid email format)  
(Field stored in report ✅)

### Validation Error Display

1. **In the chat**: When validation fails, a warning message shows what went wrong
2. **In the sidebar**: Active validation errors are shown in red under "Validation Issues"
3. **In the LLM prompt**: The LLM is aware of validation failures and adjusts its response

## Implementation Details

### Files Changed

- **`validators.py`**: New module containing the `FieldValidator` class
  - Validates all field types
  - Returns validation status and error messages
  - Can be extended for custom validation rules

- **`ui.py`**: Updated to validate fields before storing
  - Imports `FieldValidator`
  - Validates extracted fields in `handle_user_turn()`
  - Passes validation errors to LLM in system prompt
  - Displays validation errors in chat and sidebar

### Key Functions

**`FieldValidator.validate_field(field_name, value)`**
- Returns: `(is_valid: bool, error_message: str or None)`
- Validates any field and returns descriptive error messages

**`FieldValidator.get_field_type(field_name)`**
- Returns: The expected data type for a field

**`FieldValidator.get_validation_instruction(field_name)`**
- Returns: Human-readable validation help text

## Extending Validation

To add custom validation rules:

```python
# In validators.py
FIELD_TYPES = {
    'new_field': 'custom_type',
    ...
}

@classmethod
def _validate_custom_type(cls, value: str) -> Tuple[bool, Optional[str]]:
    # Your validation logic here
    if not valid:
        return False, "Error message"
    return True, None
```

## Benefits

✅ **Prevents Bad Data**: Invalid information is rejected immediately  
✅ **User Guidance**: Clear feedback on what's needed  
✅ **LLM Awareness**: The LLM knows validation failed and responds appropriately  
✅ **Professional Reports**: Only valid, complete data goes into final reports  
✅ **Flexible**: Easy to add custom validation rules for specific fields  

## Testing

To test the validation:

1. Start the application
2. In any conversation, try entering:
   - Invalid email: "ayush" (instead of "ayush@example.com")
   - Invalid phone: "123" (less than 10 digits)
   - Invalid date: "tomorrow" (instead of a proper date format)
   - Invalid amount: "lots" (instead of a number)

The system should reject these and ask for correction.

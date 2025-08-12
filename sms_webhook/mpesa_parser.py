"""
MPESA SMS Parser for SMSMobileAPI webhooks
Based on the user's existing parsing logic
"""

import re
import datetime as dt
from typing import Dict, Any, Optional
from decimal import Decimal


class MPESAParser:
    """Parser for MPESA SMS messages"""
    
    def __init__(self):
        # Kenya timezone (UTC+3)
        self.KE_TZ = dt.timezone(dt.timedelta(hours=3))
        
        # Regex patterns for different MPESA message types
        amount_rx = r'(?P<amount>[\d,]+(?:\.\d{2})?)'
        phone_rx = r'(?P<phone>(?:\+?254|0)7\d{8})'
        date_rx = r'(?P<date>\d{1,2}/\d{1,2}/\d{2,4})'
        time_rx = r'(?P<time>\d{1,2}:\d{2}\s?(?:AM|PM))'
        code_rx = r'(?P<code>[A-Z0-9]{8,12})'
        
        # MPESA message patterns
        self.patterns = [
            # received from person (with phone)
            ("received_person",
             rf'{code_rx}\s*Confirmed\.?\s*You\s*have\s*received\s*Ksh\s*{amount_rx}\s*from\s+(?P<name>.+?)\s+{phone_rx}\s*on\s*{date_rx}\s*at\s*{time_rx}',
            ),
            # sent to person (with phone)
            ("sent_person",
             rf'{code_rx}\s*Confirmed\.?\s*Ksh\s*{amount_rx}\s*sent\s*to\s+(?P<name>.+?)\s+{phone_rx}\s*on\s*{date_rx}\s*at\s*{time_rx}',
            ),
            # paid to merchant (no phone)
            ("paid_merchant",
             rf'{code_rx}\s*Confirmed\.?\s*Ksh\s*{amount_rx}\s*paid\s*to\s+(?P<name>.+?)\s*on\s*{date_rx}\s*at\s*{time_rx}',
            ),
            # received from business or person (no phone)
            ("received_business",
             rf'{code_rx}\s*Confirmed\.?\s*You\s*have\s*received\s*Ksh\s*{amount_rx}\s*from\s+(?P<name>.+?)\s*on\s*{date_rx}\s*at\s*{time_rx}',
            ),
        ]
    
    def _normalize_phone(self, phone: Optional[str]) -> Optional[str]:
        """Normalize phone number to international format"""
        if not phone:
            return None
        
        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)
        
        if digits.startswith('0'):  # 07XXXXXXXX
            return '+254' + digits[1:]
        elif digits.startswith('254'):
            return '+254' + digits[3:]
        elif len(digits) == 9 and digits.startswith('7'):
            return '+254' + digits
        elif not phone.startswith('+'):
            return '+' + digits
        
        return phone
    
    def _parse_datetime(self, date_str: Optional[str], time_str: Optional[str]) -> Optional[dt.datetime]:
        """Parse date and time strings to datetime object"""
        if not date_str or not time_str:
            return None
        
        # Try different date formats
        for date_format in ("%d/%m/%y", "%d/%m/%Y"):
            try:
                # Clean up time string
                clean_time = time_str.upper().replace(' ', '')
                dt_obj = dt.datetime.strptime(f"{date_str} {clean_time}", f"{date_format} %I:%M%p")
                return dt_obj.replace(tzinfo=self.KE_TZ)
            except ValueError:
                continue
        
        return None
    
    def parse(self, message: str, provider_hint: str = "") -> Dict[str, Any]:
        """
        Parse MPESA SMS message
        
        Args:
            message: SMS message content
            provider_hint: Additional hint about the provider (e.g., sender number)
        
        Returns:
            Dictionary with parsed MPESA transaction data
        """
        result = {
            "provider": None,
            "direction": None,
            "amount": None,
            "name": None,
            "phone": None,
            "date": None,
            "time": None,
            "tx_code": None,
            "tx_datetime_local": None,
            "parsing_confidence": 0.0,
            "parsing_errors": [],
        }
        
        if not isinstance(message, str):
            result["parsing_errors"].append("Message is not a string")
            return result
        
        # Check if this looks like MPESA
        is_mpesa = (
            "mpesa" in provider_hint.lower() or 
            "m-pesa" in message.lower() or 
            "mpesa" in message.lower()
        )
        
        if not is_mpesa:
            result["parsing_errors"].append("Message does not appear to be MPESA")
            return result
        
        result["provider"] = "MPESA"
        
        # Try to match patterns
        for pattern_name, pattern in self.patterns:
            match = re.search(pattern, message, flags=re.IGNORECASE)
            if match:
                groups = match.groupdict()
                
                # Extract amount
                amount_str = groups.get("amount")
                if amount_str:
                    try:
                        result["amount"] = Decimal(amount_str.replace(",", ""))
                    except (ValueError, TypeError):
                        result["parsing_errors"].append(f"Invalid amount format: {amount_str}")
                
                # Extract other fields
                result["name"] = (groups.get("name") or "").strip() or None
                result["phone"] = self._normalize_phone(groups.get("phone"))
                result["date"] = groups.get("date")
                result["time"] = groups.get("time")
                result["tx_code"] = groups.get("code")
                
                # Parse datetime
                result["tx_datetime_local"] = self._parse_datetime(result["date"], result["time"])
                
                # Determine direction
                if pattern_name.startswith("received"):
                    result["direction"] = "received"
                elif pattern_name.startswith("paid"):
                    result["direction"] = "paid"
                elif pattern_name.startswith("sent"):
                    result["direction"] = "sent"
                
                # Calculate confidence score
                confidence = 0.5  # Base confidence
                if result["amount"]:
                    confidence += 0.2
                if result["tx_code"]:
                    confidence += 0.2
                if result["tx_datetime_local"]:
                    confidence += 0.1
                if result["name"]:
                    confidence += 0.1
                
                result["parsing_confidence"] = min(confidence, 1.0)
                break
        else:
            result["parsing_errors"].append("No matching pattern found")
        
        return result
    
    def is_mpesa_message(self, message: str, sender_number: str = "") -> bool:
        """Check if message is likely MPESA"""
        if not isinstance(message, str):
            return False
        
        # Check sender number
        if "MPESA" in sender_number.upper():
            return True
        
        # Check message content
        message_lower = message.lower()
        mpesa_indicators = [
            "mpesa", "m-pesa", "confirmed", "ksh", "sent", "received", "paid"
        ]
        
        return any(indicator in message_lower for indicator in mpesa_indicators)


# Global parser instance
mpesa_parser = MPESAParser()

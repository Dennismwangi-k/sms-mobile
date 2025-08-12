"""
SMS Fetcher Service for SMSMobileAPI
Uses the exact working code from the user's Jupyter notebook
"""

import os
import time
import datetime as dt
import requests
import re
import pandas as pd
from decimal import Decimal
from typing import List, Dict, Any, Optional
from django.conf import settings
from django.utils import timezone
from .models import SMSMessage, MPESATransaction


class SMSFetcher:
    """Service to fetch SMS messages from SMSMobileAPI using the exact working code"""
    
    def __init__(self):
        self.base_url = "https://api.smsmobileapi.com"
        self.api_key = getattr(settings, 'SMSMOBILE_API_KEY', '')
        
        if not self.api_key:
            raise ValueError("SMSMOBILE_API_KEY not configured in settings")
        
        # Set timezone for MPESA parsing
        self.ke_tz = dt.timezone(dt.timedelta(hours=3))  # Africa/Nairobi
        
        # MPESA parsing patterns (exact from your code)
        amount_rx = r'(?P<amount>[\d,]+(?:\.\d{2})?)'
        phone_rx  = r'(?P<phone>(?:\+?254|0)7\d{8})'
        date_rx   = r'(?P<date>\d{1,2}/\d{1,2}/\d{2,4})'
        time_rx   = r'(?P<time>\d{1,2}:\d{2}\s?(?:AM|PM))'
        code_rx   = r'(?P<code>[A-Z0-9]{8,12})'
        
        # NOTE: use \s* around punctuation to allow "Confirmed.You" (no space)
        self.mpesa_patterns = [
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
            # received from business or person (no phone; handles "via FLEX MONEY TRANSFER")
            ("received_business",
             rf'{code_rx}\s*Confirmed\.?\s*You\s*have\s*received\s*Ksh\s*{amount_rx}\s*from\s+(?P<name>.+?)\s*on\s*{date_rx}\s*at\s*{time_rx}',
            ),
        ]
    
    def _unwrap_sms(self, payload):
        """Extract SMS list from API response - exact code from user"""
        if isinstance(payload, list): 
            return payload
        if isinstance(payload, dict):
            if isinstance(payload.get("result"), dict) and isinstance(payload["result"].get("sms"), list):
                return payload["result"]["sms"]
            if isinstance(payload.get("sms"), list):
                return payload["sms"]
        return []
    
    def _to_unix(self, message):
        """Convert timestamp to Unix timestamp - exact code from user"""
        # prefer numeric timestamp fields
        for k in ("timestamp_unix", "time", "ts"):
            if k in message:
                try:
                    return int(str(message[k])[:10])
                except:
                    pass
        
        tr = str(message.get("time_received", ""))
        if tr.isdigit() and len(tr) == 13:
            return int(int(tr) / 1000)
        if tr.isdigit() and len(tr) == 10:
            return int(tr)
        
        # "YYYYMMDDHHMMSSmmm"
        if len(tr) >= 14 and tr[:4].isdigit():
            try:
                return int(dt.datetime.strptime(tr[:14], "%Y%m%d%H%M%S").timestamp())
            except:
                pass
        
        # combine "date"+"hour"
        if message.get("date") and message.get("hour"):
            try:
                return int(dt.datetime.fromisoformat(f"{message['date']} {message['hour']}").timestamp())
            except:
                pass
        
        return int(time.time())
    
    def fetch_inbox(self, only_unread=False, device_id=None, after_ts=0):
        """Fetch SMS messages from SMSMobileAPI - exact code from user"""
        params = {"apikey": self.api_key}
        
        if only_unread: 
            params["onlyunread"] = "yes"
        if device_id: 
            params["sIdentifiantPhone"] = device_id
        if after_ts: 
            params["after_timestamp_unix"] = int(after_ts)
        
        try:
            print(f"🔍 Making API request to: {self.base_url}/getsms/")
            print(f"🔑 Using API key: {self.api_key[:10]}...")
            print(f"📋 Parameters: {params}")
            
            response = requests.get(f"{self.base_url}/getsms/", params=params, timeout=30)
            print(f"📡 Response status: {response.status_code}")
            
            response.raise_for_status()
            response_data = response.json()
            print(f"📦 Response data type: {type(response_data)}")
            print(f"📦 Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Not a dict'}")
            
            unwrapped = self._unwrap_sms(response_data)
            print(f"📱 Unwrapped SMS count: {len(unwrapped)}")
            
            return unwrapped
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return []
    
    def normalize(self, records):
        """Normalize SMS records - exact code from user"""
        rows = []
        for m in records:
            ts = self._to_unix(m)
            rows.append({
                "received_at": dt.datetime.utcfromtimestamp(ts).isoformat() + "Z",
                "number": m.get("number", ""),
                "message": m.get("message", ""),
                "guid": m.get("guid") or m.get("guid_message") or "",
                "device_id": m.get("sIdentifiantPhone") or m.get("device_id") or "",
                "timestamp_unix": ts,
                "raw_data": m
            })
        
        # Create DataFrame and sort (exact from your code)
        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.sort_values("timestamp_unix", ascending=False).reset_index(drop=True)
        
        return df
    
    def _norm_phone(self, p: Optional[str]) -> Optional[str]:
        """Normalize phone number - exact from your code"""
        if not p: return None
        digits = re.sub(r'\D', '', p)
        if digits.startswith('0'):   # 07XXXXXXXX
            return '+254' + digits[1:]
        if digits.startswith('254'):
            return '+254' + digits[3:]
        if len(digits) == 9 and digits.startswith('7'):
            return '+254' + digits
        return '+' + digits if not p.startswith('+') else p

    def _to_iso_local(self, d: Optional[str], t: Optional[str]) -> Optional[str]:
        """Convert date and time to ISO local - exact from your code"""
        if not d or not t: return None
        for dp in ("%d/%m/%y", "%d/%m/%Y"):
            try:
                dt_obj = dt.datetime.strptime(f"{d} {t.upper().replace(' ', '')}", f"{dp} %I:%M%p")
                return dt_obj.replace(tzinfo=self.ke_tz).isoformat()
            except Exception:
                continue
        return None

    def parse_mpesa(self, text: str, provider_hint: str = "") -> dict:
        """Parse MPESA message - exact from your code"""
        out = {
            "provider": "MPESA" if ("mpesa" in provider_hint.lower() or "m-pesa" in text.lower() or "mpesa" in text.lower()) else None,
            "direction": None,
            "amount": None,
            "name": None,
            "phone": None,
            "date": None,
            "time": None,
            "tx_code": None,
            "tx_datetime_local": None,
        }
        if not isinstance(text, str):
            return out
        for key, pat in self.mpesa_patterns:
            m = re.search(pat, text, flags=re.IGNORECASE)
            if not m:
                continue
            g = m.groupdict()
            amt = g.get("amount")
            out["amount"] = float(amt.replace(",", "")) if amt else None
            out["name"] = (g.get("name") or "").strip() or None
            out["phone"] = self._norm_phone(g.get("phone"))
            out["date"] = g.get("date")
            out["time"] = g.get("time")
            out["tx_code"] = g.get("code")
            out["tx_datetime_local"] = self._to_iso_local(out["date"], out["time"])
            out["direction"] = "received" if key.startswith("received") else ("paid" if key.startswith("paid") else "sent")
            if out["provider"] is None:
                out["provider"] = "MPESA"
            break
        return out
    
    def fetch_and_store_sms(self, only_unread=False, device_id=None, after_ts=0):
        """Fetch SMS messages and store them in the database using exact working code"""
        print(f"📱 Fetching SMS messages from SMSMobileAPI (unread only: {only_unread})...")
        
        # Fetch messages using exact working code
        raw_messages = self.fetch_inbox(only_unread, device_id, after_ts)
        
        if not raw_messages:
            print("❌ No messages found")
            return []
        
        print(f"✅ Found {len(raw_messages)} raw messages")
        
        # Normalize using exact working code
        df_inbox = self.normalize(raw_messages)
        print(f"✅ Normalized {len(df_inbox)} messages")
        
        # Show first few messages like in your notebook
        if not df_inbox.empty:
            print("\n📋 First 3 messages:")
            display_cols = ["received_at", "number", "message", "guid", "device_id"]
            for i, row in df_inbox[display_cols].head(3).iterrows():
                print(f"  {i+1}. From: {row['number']}")
                print(f"     Message: {row['message'][:100]}...")
                print(f"     GUID: {row['guid']}")
                print()
        
        # Parse MPESA messages (exact from your code)
        print("🔍 Parsing MPESA messages...")
        mpesa_mask = (
            df_inbox["number"].str.contains("MPESA", case=False, na=False) |
            df_inbox["message"].str.contains(r"\bM-?PESA\b", case=False, na=False)
        )
        
        mpesa_messages = df_inbox.loc[mpesa_mask]
        print(f"💰 Found {len(mpesa_messages)} MPESA messages")
        
        # Parse each MPESA message
        parsed_mpesa = []
        for idx, row in mpesa_messages.iterrows():
            parsed = self.parse_mpesa(row["message"], row.get("number", ""))
            parsed_mpesa.append(parsed)
            print(f"  📱 Parsed: {parsed['direction']} Ksh {parsed['amount']} from {parsed['name']}")
        
        # Store messages in database
        stored_messages = []
        new_mpesa_transactions = []
        
        for idx, row in df_inbox.iterrows():
            # Check if message already exists
            existing_sms = SMSMessage.objects.filter(guid=row["guid"]).first()
            
            if existing_sms:
                print(f"⏭️ SMS with GUID {row['guid']} already exists, skipping...")
                continue
            
            try:
                # Parse the ISO timestamp
                received_time = dt.datetime.fromisoformat(row["received_at"].replace('Z', '+00:00'))
                
                # Create SMS message record
                sms_message = SMSMessage.objects.create(
                    guid=row["guid"],
                    number=row["number"],
                    message=row["message"],
                    date=received_time.date(),
                    hour=received_time.time(),
                    time_received=received_time,
                    raw_payload=row["raw_data"]
                )
                
                stored_messages.append(sms_message)
                print(f"✅ Stored SMS: {row['guid']} from {row['number']}")
                
                # Check if this is an MPESA message and create transaction
                if mpesa_mask.iloc[idx]:
                    # Find the parsed data for this message
                    mpesa_idx = mpesa_messages.index.get_loc(idx)
                    parsed_data = parsed_mpesa[mpesa_idx]
                    
                    if parsed_data["direction"]:
                        mpesa_tx = MPESATransaction.objects.create(
                            sms_message=sms_message,
                            provider=parsed_data["provider"],
                            direction=parsed_data["direction"],
                            amount=parsed_data["amount"],
                            name=parsed_data["name"],
                            phone=parsed_data["phone"],
                            tx_code=parsed_data["tx_code"],
                            tx_date=parsed_data["date"],
                            tx_time=parsed_data["time"],
                            tx_datetime_local=parsed_data["tx_datetime_local"],
                            parsing_confidence=1.0,
                            parsing_errors=""
                        )
                        
                        new_mpesa_transactions.append(mpesa_tx)
                        sms_message.mark_as_processed("Successfully parsed as MPESA transaction")
                        print(f"   💰 Created MPESA transaction: {parsed_data['direction']} Ksh {parsed_data['amount']}")
                    else:
                        sms_message.mark_as_failed("Failed to parse MPESA transaction")
                        print(f"   ❌ MPESA parsing failed")
                else:
                    sms_message.mark_as_processed("SMS received (not MPESA)")
                    print(f"   📨 Regular SMS stored")
                
            except Exception as e:
                print(f"❌ Error storing SMS {row['guid']}: {e}")
                continue
        
        print(f"🎉 Successfully stored {len(stored_messages)} new SMS messages")
        print(f"💰 Created {len(new_mpesa_transactions)} new MPESA transactions")
        
        return stored_messages
    
    def get_latest_timestamp(self):
        """Get the latest timestamp from stored SMS messages"""
        latest_sms = SMSMessage.objects.order_by('-time_received').first()
        if latest_sms:
            return int(latest_sms.time_received.timestamp())
        return 0
    
    def sync_recent_messages(self, hours_back=24):
        """Sync recent messages from the last N hours"""
        cutoff_time = timezone.now() - timezone.timedelta(hours=hours_back)
        cutoff_timestamp = int(cutoff_time.timestamp())
        
        return self.fetch_and_store_sms(after_ts=cutoff_timestamp)
    
    def get_sms_summary(self):
        """Get a summary of SMS messages like in the Jupyter notebook"""
        raw_messages = self.fetch_inbox(only_unread=False)
        if not raw_messages:
            return {"count": 0, "messages": []}
        
        df_inbox = self.normalize(raw_messages)
        
        # Get MPESA messages
        mpesa_mask = (
            df_inbox["number"].str.contains("MPESA", case=False, na=False) |
            df_inbox["message"].str.contains(r"\bM-?PESA\b", case=False, na=False)
        )
        mpesa_messages = df_inbox.loc[mpesa_mask]
        
        return {
            "total_count": len(df_inbox),
            "mpesa_count": len(mpesa_messages),
            "messages": df_inbox.to_dict('records')[:50],  # First 50 for display
            "mpesa_messages": mpesa_messages.to_dict('records')[:20]  # First 20 MPESA for display
        }


# Global fetcher instance
sms_fetcher = SMSFetcher()

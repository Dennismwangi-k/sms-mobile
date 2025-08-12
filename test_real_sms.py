#!/usr/bin/env python3
"""
Test script for real SMS fetching from SMSMobileAPI
This script shows how to use your exact working code with the Django system
"""

import os
import sys
import django
import time
import datetime as dt
import requests
import re
import pandas as pd

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smswebhook.settings')
django.setup()

def test_smsmobile_api_directly():
    """Test SMSMobileAPI directly using your exact working code"""
    print("🧪 Testing SMSMobileAPI Directly (Your Working Code)")
    print("=" * 60)
    
    # Your exact working code
    BASE = "https://api.smsmobileapi.com"
    API_KEY = os.getenv("SMSMOBILE_API_KEY")
    
    if not API_KEY:
        print("❌ SMSMOBILE_API_KEY not set in environment")
        print("Please set your real API key:")
        print("export SMSMOBILE_API_KEY='your-actual-key-here'")
        return False
    
    print(f"✅ Using API Key: {API_KEY[:10]}...")
    
    # Your exact helper functions
    def _unwrap_sms(payload):
        if isinstance(payload, list): return payload
        if isinstance(payload, dict):
            if isinstance(payload.get("result"), dict) and isinstance(payload["result"].get("sms"), list):
                return payload["result"]["sms"]
            if isinstance(payload.get("sms"), list):
                return payload["sms"]
        return []

    def _to_unix(m):
        # prefer numeric timestamp fields
        for k in ("timestamp_unix", "time", "ts"):
            if k in m:
                try: return int(str(m[k])[:10])
                except: pass
        tr = str(m.get("time_received",""))
        if tr.isdigit() and len(tr) == 13: return int(int(tr)/1000)
        if tr.isdigit() and len(tr) == 10: return int(tr)
        # "YYYYMMDDHHMMSSmmm"
        if len(tr) >= 14 and tr[:4].isdigit():
            try: return int(dt.datetime.strptime(tr[:14], "%Y%m%d%H%M%S").timestamp())
            except: pass
        # combine "date"+"hour"
        if m.get("date") and m.get("hour"):
            try: return int(dt.datetime.fromisoformat(f"{m['date']} {m['hour']}").timestamp())
            except: pass
        return int(time.time())

    def fetch_inbox(only_unread=False, device_id=None, after_ts=0):
        params = {"apikey": API_KEY}
        if only_unread: params["onlyunread"] = "yes"
        if device_id: params["sIdentifiantPhone"] = device_id
        if after_ts: params["after_timestamp_unix"] = int(after_ts)
        r = requests.get(f"{BASE}/getsms/", params=params, timeout=30)
        r.raise_for_status()
        return _unwrap_sms(r.json())

    def normalize(records):
        rows = []
        for m in records:
            ts = _to_unix(m)
            rows.append({
                "received_at": dt.datetime.utcfromtimestamp(ts).isoformat() + "Z",
                "number": m.get("number",""),
                "message": m.get("message",""),
                "guid": m.get("guid") or m.get("guid_message") or "",
                "device_id": m.get("sIdentifiantPhone") or m.get("device_id") or "",
                "timestamp_unix": ts,
            })
        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.sort_values("timestamp_unix", ascending=False).reset_index(drop=True)
        return df

    try:
        print("📱 Fetching SMS messages from SMSMobileAPI...")
        recs = fetch_inbox(only_unread=False)
        
        if not recs:
            print("❌ No messages found. This could mean:")
            print("   - The API key is invalid")
            print("   - No SMS messages in the system")
            print("   - API endpoint is not responding")
            return False
        
        print(f"✅ Found {len(recs)} raw messages")
        
        # Show first few messages
        print("\n📋 First 3 messages:")
        for i, msg in enumerate(recs[:3]):
            print(f"  {i+1}. From: {msg.get('number', 'Unknown')}")
            print(f"     Message: {msg.get('message', '')[:100]}...")
            print(f"     GUID: {msg.get('guid', 'N/A')}")
            print()
        
        # Normalize messages
        print("🔄 Normalizing messages...")
        df_inbox = normalize(recs)
        print(f"✅ Normalized {len(df_inbox)} messages")
        
        # Show normalized data
        if not df_inbox.empty:
            print("\n📊 Normalized data (first 3 rows):")
            print(df_inbox[["received_at","number","message","guid","device_id"]].head(3))
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_django_integration():
    """Test the Django integration with SMSMobileAPI"""
    print("\n🧪 Testing Django Integration")
    print("=" * 40)
    
    try:
        from sms_webhook.sms_fetcher import sms_fetcher
        
        print("✅ SMS Fetcher imported successfully")
        
        # Test fetching and storing
        print("📱 Testing SMS fetch and store...")
        new_messages = sms_fetcher.fetch_and_store_sms(only_unread=False)
        
        print(f"✅ Django integration working: {len(new_messages)} messages processed")
        
        return True
        
    except Exception as e:
        print(f"❌ Django integration error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Real SMS Fetching Test Suite")
    print("=" * 40)
    
    # Test 1: Direct API access
    if test_smsmobile_api_directly():
        print("✅ Direct API test passed")
    else:
        print("❌ Direct API test failed")
        print("\n💡 To fix this:")
        print("1. Get your real SMSMobileAPI key")
        print("2. Set it: export SMSMOBILE_API_KEY='your-key'")
        print("3. Make sure you have SMS messages in your account")
        return
    
    # Test 2: Django integration
    if test_django_integration():
        print("✅ Django integration test passed")
    else:
        print("❌ Django integration test failed")
    
    print("\n🎯 Next Steps:")
    print("1. Set your real SMSMobileAPI key in .env file")
    print("2. Run: python3 manage.py fetch_sms")
    print("3. Check the dashboard at http://localhost:8000/")
    print("4. Use the 'Fetch New SMS' button for real-time updates")

if __name__ == "__main__":
    main()

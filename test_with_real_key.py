#!/usr/bin/env python3
"""
Test script for real SMSMobileAPI key
This shows exactly what you need to do to get real SMS messages
"""

import os
import sys
import requests
import json
from decouple import config

def test_api_key():
    """Test if your API key is working"""
    print("🔑 Testing SMSMobileAPI Key")
    print("=" * 40)
    
    # Get API key from .env file using python-decouple (same as Django)
    api_key = config('SMSMOBILE_API_KEY', default='')
    
    if not api_key:
        print("❌ No API key found in .env file!")
        print("\n💡 To fix this:")
        print("1. Get your real API key from https://api.smsmobileapi.com")
        print("2. Set it in your .env file:")
        print("   SMSMOBILE_API_KEY=your-real-key-here")
        print("3. Or export it as environment variable:")
        print("   export SMSMOBILE_API_KEY='your-real-key-here'")
        return False
    
    print(f"✅ Found API key: {api_key[:10]}...")
    
    # Test the API directly
    base_url = "https://api.smsmobileapi.com"
    params = {"apikey": api_key}
    
    try:
        print(f"\n📡 Testing API endpoint: {base_url}/getsms/")
        print(f"🔑 Using key: {api_key[:10]}...")
        
        response = requests.get(f"{base_url}/getsms/", params=params, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API call successful!")
            print(f"📦 Response structure: {list(data.keys())}")
            
            # Check for SMS messages
            if "result" in data and "sms" in data["result"]:
                sms_count = len(data["result"]["sms"])
                print(f"📱 Found {sms_count} SMS messages!")
                
                if sms_count > 0:
                    print("\n📋 First SMS message:")
                    first_sms = data["result"]["sms"][0]
                    print(f"   From: {first_sms.get('number', 'Unknown')}")
                    print(f"   Message: {first_sms.get('message', '')[:100]}...")
                    print(f"   GUID: {first_sms.get('guid', 'N/A')}")
                    print(f"   Time: {first_sms.get('time_received', 'N/A')}")
                    
                    return True
                else:
                    print("📭 No SMS messages found in your account")
                    print("💡 This could mean:")
                    print("   - Your account is new and has no SMS yet")
                    print("   - All messages are marked as read")
                    print("   - You need to send some SMS to test")
                    return False
            else:
                print("❌ Unexpected response structure")
                print(f"📦 Full response: {json.dumps(data, indent=2)}")
                return False
                
        elif response.status_code == 401:
            print("❌ Unauthorized - Invalid API key")
            print("💡 Check your API key is correct")
            return False
        elif response.status_code == 403:
            print("❌ Forbidden - API key doesn't have permission")
            print("💡 Check your account permissions")
            return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"📦 Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_next_steps():
    """Show what to do next"""
    print("\n🎯 Next Steps:")
    print("1. ✅ Get your real API key from SMSMobileAPI dashboard")
    print("2. ✅ Set it in .env file: SMSMOBILE_API_KEY=your-real-key")
    print("3. ✅ Test again: python3 test_with_real_key.py")
    print("4. ✅ Run Django command: python3 manage.py fetch_sms")
    print("5. ✅ Check dashboard: http://localhost:8000/")
    print("6. ✅ Use 'Fetch New SMS' button for real-time updates")

def main():
    """Main test function"""
    print("🚀 SMSMobileAPI Real Key Test")
    print("=" * 40)
    
    if test_api_key():
        print("\n🎉 SUCCESS! Your API key is working!")
        print("💡 Now you can:")
        print("   - Run: python3 manage.py fetch_sms")
        print("   - Check the dashboard for real SMS")
        print("   - Use the web interface to fetch messages")
    else:
        print("\n❌ API key test failed")
        show_next_steps()

if __name__ == "__main__":
    main()

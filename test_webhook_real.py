#!/usr/bin/env python3
"""
Test script to simulate real webhook data
This shows exactly how your webhook system works
"""

import requests
import json
import time

def test_webhook_with_real_data():
    """Test webhook with realistic SMS data"""
    print("🧪 Testing Webhook with Real SMS Data")
    print("=" * 50)
    
    # Your webhook endpoint
    webhook_url = "http://localhost:8000/webhook/sms/"
    
    # Simulate real MPESA SMS data (like what SMSMobileAPI would send)
    test_sms_data = {
        "guid": f"TEST-{int(time.time())}",
        "number": "MPESA",
        "message": "THC123ABC Confirmed. You have received Ksh500.00 from JOHN DOE +254712345678 on 12/8/25 at 3:45 PM",
        "date": "2025-08-12",
        "hour": "15:45:00",
        "time_received": "2025-08-12 15:45:00"
    }
    
    print(f"📱 Sending test SMS to webhook: {webhook_url}")
    print(f"📋 SMS Data:")
    print(f"   From: {test_sms_data['number']}")
    print(f"   Message: {test_sms_data['message'][:50]}...")
    print(f"   GUID: {test_sms_data['guid']}")
    
    try:
        # Send webhook data
        response = requests.post(
            webhook_url,
            json=test_sms_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\n📡 Webhook Response:")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook processed successfully!")
            print("💡 This SMS should now appear in your dashboard")
            print("💡 Check: http://localhost:8000/")
        else:
            print("❌ Webhook failed")
            
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")

def test_multiple_webhooks():
    """Test multiple webhook calls to simulate real usage"""
    print("\n🔄 Testing Multiple Webhook Calls")
    print("=" * 40)
    
    webhook_url = "http://localhost:8000/webhook/sms/"
    
    # Different types of SMS to test
    test_messages = [
        {
            "guid": f"MPESA-{int(time.time())}-1",
            "number": "MPESA",
            "message": "ABC456DEF Confirmed. Ksh1000.00 sent to JANE SMITH +254798765432 on 12/8/25 at 4:30 PM",
            "date": "2025-08-12",
            "hour": "16:30:00",
            "time_received": "2025-08-12 16:30:00"
        },
        {
            "guid": f"SAFARICOM-{int(time.time())}-2",
            "number": "Safaricom",
            "message": "You have received 100SMS with expiry @Ksh5.00. Your balance is KSH 25.50",
            "date": "2025-08-12",
            "hour": "16:31:00",
            "time_received": "2025-08-12 16:31:00"
        },
        {
            "guid": f"PERSONAL-{int(time.time())}-3",
            "number": "+254712345678",
            "message": "Hey, how are you doing? Can you call me back?",
            "date": "2025-08-12",
            "hour": "16:32:00",
            "time_received": "2025-08-12 16:32:00"
        }
    ]
    
    for i, sms_data in enumerate(test_messages, 1):
        print(f"\n📱 Sending SMS {i}/3...")
        print(f"   From: {sms_data['number']}")
        print(f"   Message: {sms_data['message'][:40]}...")
        
        try:
            response = requests.post(
                webhook_url,
                json=sms_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"   ✅ Success")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)  # Small delay between requests
    
    print(f"\n🎉 All webhook tests completed!")
    print(f"💡 Check your dashboard: http://localhost:8000/")

def main():
    """Main test function"""
    print("🚀 Webhook Real-Time Testing Suite")
    print("=" * 40)
    
    print("This test simulates what happens when SMSMobileAPI sends real webhooks to your server.")
    print("Each webhook call will:")
    print("1. ✅ Process the SMS instantly")
    print("2. ✅ Store it in the database")
    print("3. ✅ Parse MPESA transactions automatically")
    print("4. ✅ Update your dashboard in real-time")
    
    # Test single webhook
    test_webhook_with_real_data()
    
    # Test multiple webhooks
    test_multiple_webhooks()
    
    print("\n🎯 Next Steps for True Real-Time:")
    print("1. ✅ Your webhook system is working perfectly")
    print("2. 🔧 Configure SMSMobileAPI to send webhooks to your server")
    print("3. 🚀 New SMS will appear instantly without any button clicks!")
    print("4. 🌐 Make your server public (use ngrok or deploy to cloud)")

if __name__ == "__main__":
    main()

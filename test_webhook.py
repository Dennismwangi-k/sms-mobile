#!/usr/bin/env python3
"""
Test script for SMS Webhook functionality
Run this script to test the webhook endpoint with sample MPESA SMS data
"""

import requests
import json
import time
from datetime import datetime

# Configuration
WEBHOOK_URL = "http://localhost:8000/webhook/sms/"
BASE_URL = "http://localhost:8000"

def test_webhook_with_mpesa_sms():
    """Test webhook with sample MPESA SMS messages"""
    
    # Sample MPESA SMS messages
    test_messages = [
        {
            "date": "2025-01-20",
            "hour": "10:15:00",
            "time_received": "2025-01-20 10:14:50",
            "message": "ABC12345 Confirmed. You have received Ksh 5,000.00 from John Doe +254712345678 on 20/01/25 at 10:15 AM",
            "number": "MPESA",
            "guid": "test_guid_001"
        },
        {
            "date": "2025-01-20",
            "hour": "11:30:00",
            "time_received": "2025-01-20 11:29:45",
            "message": "XYZ98765 Confirmed. Ksh 2,500.00 sent to Jane Smith +254798765432 on 20/01/25 at 11:30 AM",
            "number": "MPESA",
            "guid": "test_guid_002"
        },
        {
            "date": "2025-01-20",
            "hour": "14:45:00",
            "time_received": "2025-01-20 14:44:30",
            "message": "DEF45678 Confirmed. Ksh 1,000.00 paid to ShopRite Supermarket on 20/01/25 at 2:45 PM",
            "number": "MPESA",
            "guid": "test_guid_003"
        },
        {
            "date": "2025-01-20",
            "hour": "16:20:00",
            "time_received": "2025-01-20 16:19:15",
            "message": "GHI78901 Confirmed. You have received Ksh 15,000.00 from Business Corp Ltd on 20/01/25 at 4:20 PM",
            "number": "MPESA",
            "guid": "test_guid_004"
        }
    ]
    
    print("🚀 Testing SMS Webhook with MPESA Messages")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📱 Testing Message {i}: {message['guid']}")
        print(f"   Content: {message['message'][:60]}...")
        
        try:
            # Send webhook request
            response = requests.post(
                WEBHOOK_URL,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"   ✅ Success: {response.json()}")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
        
        # Small delay between requests
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("🎯 Webhook testing completed!")

def test_dashboard_access():
    """Test if the dashboard is accessible"""
    
    print("\n🌐 Testing Dashboard Access")
    print("=" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard accessible")
        else:
            print(f"❌ Dashboard error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Dashboard access failed: {e}")

def test_api_endpoints():
    """Test API endpoints"""
    
    print("\n🔌 Testing API Endpoints")
    print("=" * 30)
    
    endpoints = [
        "/api/sms/",
        "/api/mpesa/",
        "/api/mpesa/statistics/"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint} - Accessible")
            else:
                print(f"❌ {endpoint} - Error: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - Failed: {e}")

def main():
    """Main test function"""
    
    print("🧪 SMS Webhook Testing Suite")
    print("=" * 40)
    print(f"Target URL: {WEBHOOK_URL}")
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print("\n❌ Server not responding properly")
            return
    except requests.exceptions.RequestException:
        print("\n❌ Server not accessible. Make sure Django is running on localhost:8000")
        print("   Run: python manage.py runserver")
        return
    
    print("\n✅ Server is running and accessible")
    
    # Run tests
    test_webhook_with_mpesa_sms()
    test_dashboard_access()
    test_api_endpoints()
    
    print("\n🎉 All tests completed!")
    print("\n📊 Check the dashboard at: http://localhost:8000/")
    print("🔍 View SMS messages at: http://localhost:8000/sms/")
    print("💰 View MPESA transactions at: http://localhost:8000/mpesa/")
    print("⚙️  Admin interface at: http://localhost:8000/admin/")

if __name__ == "__main__":
    main()

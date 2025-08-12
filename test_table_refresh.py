#!/usr/bin/env python3
"""
Test script to debug the SMS table refresh functionality
"""

import requests
import json
import time

def test_sms_table_api():
    """Test the SMS table API endpoint"""
    print("🧪 Testing SMS Table API Endpoint")
    print("=" * 50)
    
    # Test the API endpoint
    url = "http://localhost:8000/api/sms-table/"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"📡 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                print(f"📊 SMS Messages Count: {len(data.get('sms_messages', []))}")
                print(f"📄 Pagination: Page {data.get('pagination', {}).get('current_page')} of {data.get('pagination', {}).get('total_pages')}")
            else:
                print(f"❌ API Error: {data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
        print(f"Raw Response: {response.text}")

def test_dashboard_data():
    """Test the dashboard data API endpoint"""
    print("\n🧪 Testing Dashboard Data API Endpoint")
    print("=" * 50)
    
    url = "http://localhost:8000/api/dashboard-data/"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"📡 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
        print(f"Raw Response: {response.text}")

def test_webhook_endpoint():
    """Test the webhook endpoint with a test SMS"""
    print("\n🧪 Testing Webhook Endpoint")
    print("=" * 50)
    
    url = "http://localhost:8000/webhook/sms/"
    
    # Test SMS data
    test_sms = {
        "guid": f"DEBUG-TEST-{int(time.time())}",
        "number": "TEST-NUMBER",
        "message": "This is a test SMS for debugging table refresh",
        "date": "2025-08-12",
        "hour": "16:45:00",
        "time_received": "2025-08-12 16:45:00"
    }
    
    try:
        response = requests.post(url, json=test_sms, headers={'Content-Type': 'application/json'}, timeout=10)
        print(f"📡 Webhook Response Status: {response.status_code}")
        print(f"📋 Test SMS Data: {json.dumps(test_sms, indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Webhook Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")

if __name__ == "__main__":
    print("🚀 SMS Table Refresh Debug Test Suite")
    print("=" * 60)
    
    # Test all endpoints
    test_sms_table_api()
    test_dashboard_data()
    test_webhook_endpoint()
    
    print("\n🎯 Debug Test Complete!")
    print("💡 Check the browser console for JavaScript errors")
    print("💡 Open http://localhost:8000/ and click 'Refresh Table' button")

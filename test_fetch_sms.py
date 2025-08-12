#!/usr/bin/env python3
"""
Test script for SMS fetching functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smswebhook.settings')
django.setup()

from sms_webhook.sms_fetcher import sms_fetcher

def test_sms_fetching():
    """Test SMS fetching functionality"""
    print("🧪 Testing SMS Fetching from SMSMobileAPI")
    print("=" * 50)
    
    try:
        # Test fetching SMS messages
        print("📱 Fetching SMS messages...")
        new_messages = sms_fetcher.fetch_and_store_sms(only_unread=False)
        
        print(f"✅ Successfully fetched {len(new_messages)} new SMS messages")
        
        if new_messages:
            print("\n📋 New messages:")
            for i, msg in enumerate(new_messages, 1):
                print(f"  {i}. {msg.number}: {msg.message[:50]}...")
        
        # Test syncing recent messages
        print("\n🔄 Testing recent message sync...")
        recent_messages = sms_fetcher.sync_recent_messages(hours_back=24)
        print(f"✅ Synced {len(recent_messages)} recent messages")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 SMS Fetching Test Suite")
    print("=" * 30)
    
    # Check if API key is configured
    if not os.getenv('SMSMOBILE_API_KEY'):
        print("❌ SMSMOBILE_API_KEY not configured")
        print("Please set the environment variable or add it to your .env file")
        return
    
    print("✅ SMSMOBILE_API_KEY is configured")
    
    # Run tests
    if test_sms_fetching():
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()

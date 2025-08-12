# 🚀 Real SMS Setup Guide

## Overview
This guide shows you how to integrate your working SMSMobileAPI code with the Django dashboard to fetch and display real SMS messages in real-time.

## 🔑 Step 1: Get Your Real SMSMobileAPI Key

1. **Login to SMSMobileAPI Dashboard**
   - Go to https://api.smsmobileapi.com
   - Sign in to your account

2. **Get Your API Key**
   - Navigate to API settings
   - Copy your API key

3. **Set the API Key**
   ```bash
   # Option 1: Set in .env file
   echo "SMSMOBILE_API_KEY=your-actual-api-key-here" >> .env
   
   # Option 2: Set as environment variable
   export SMSMOBILE_API_KEY="your-actual-api-key-here"
   ```

## 📱 Step 2: Test Your API Key

Run the test script to verify your API key works:

```bash
python3 test_real_sms.py
```

**Expected Output:**
```
✅ Using API Key: your-actua...
📱 Fetching SMS messages from SMSMobileAPI...
✅ Found X raw messages

📋 First 3 messages:
  1. From: MPESA
     Message: THC343MHYD Confirmed. You have received Ksh300...
     GUID: D55A32B7-DEA9-4BB5-A49F-6ECE2FDB4439
```

## 🎯 Step 3: Fetch Real SMS Messages

### Option A: Command Line
```bash
# Fetch all SMS messages
python3 manage.py fetch_sms

# Fetch only unread messages
python3 manage.py fetch_sms --unread-only

# Sync recent messages (last 24 hours)
python3 manage.py fetch_sms --sync-recent

# Sync specific time range
python3 manage.py fetch_sms --sync-recent --hours-back 48
```

### Option B: Web Dashboard
1. Open http://localhost:8000/
2. Click the **"Fetch New SMS"** button
3. Watch real-time updates

### Option C: API Endpoint
```bash
curl -X POST http://localhost:8000/api/fetch-sms/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your-csrf-token"
```

## 🔄 Step 4: Real-Time Features

### Auto-Refresh Dashboard
- Dashboard automatically refreshes every 30 seconds
- Statistics update in real-time
- No page reload needed

### Live Status Indicators
- Green dot: Real-time active
- Blue flash: Data updated
- Last update timestamp

### Real-Time SMS Table
- Shows all SMS messages with pagination
- Automatic MPESA parsing
- Status indicators for each message

## 📊 Step 5: Monitor Your Data

### Dashboard Statistics
- **Total SMS**: Count of all messages
- **MPESA Transactions**: Parsed financial transactions
- **Unprocessed**: Messages awaiting processing

### SMS Table Features
- **Time**: When message was received
- **Number**: Sender number/name
- **Message**: Full message content
- **Status**: Processing status
- **Direction**: Message direction
- **GUID**: Unique identifier

### MPESA Parsing
- **Automatic Detection**: Identifies MPESA messages
- **Transaction Details**: Amount, sender, code, time
- **Direction**: Received, sent, or paid
- **Confidence**: Parsing accuracy

## 🛠️ Step 6: Customization

### Modify MPESA Patterns
Edit `sms_webhook/mpesa_parser.py` to add new patterns:

```python
MPESA_PATTERNS = [
    # Add your custom patterns here
    ("custom_pattern",
     r'your-regex-pattern-here'),
]
```

### Adjust Fetch Frequency
Modify the auto-refresh interval in `templates/sms_webhook/dashboard.html`:

```javascript
// Change from 30 seconds to your preferred interval
setInterval(() => {
    refreshDashboardData();
}, 60000); // 60 seconds
```

### Add New SMS Sources
Modify `sms_webhook/sms_fetcher.py` to add new SMS sources:

```python
def fetch_from_multiple_sources(self):
    """Fetch from multiple SMS sources"""
    sources = [
        self.fetch_inbox(only_unread=False),
        self.fetch_from_another_api(),
        # Add more sources here
    ]
    return [msg for source in sources for msg in source]
```

## 🚨 Troubleshooting

### "No messages found"
- Check your API key is correct
- Verify you have SMS messages in your account
- Check API endpoint is accessible

### "API key not configured"
- Set SMSMOBILE_API_KEY in .env file
- Or export as environment variable
- Restart Django server

### "Permission denied"
- Check API key permissions
- Verify account is active
- Contact SMSMobileAPI support

### "Connection timeout"
- Check internet connection
- Verify API endpoint URL
- Try again later

## 📈 Performance Tips

### Optimize Fetch Frequency
- Start with 30-second intervals
- Adjust based on message volume
- Use longer intervals for low-traffic periods

### Batch Processing
- Fetch multiple messages at once
- Use pagination for large datasets
- Implement rate limiting if needed

### Caching
- Cache frequently accessed data
- Store parsed results
- Use Redis for high-performance caching

## 🔐 Security Considerations

### API Key Protection
- Never commit API keys to version control
- Use environment variables
- Rotate keys regularly

### Access Control
- Restrict dashboard access
- Implement user authentication
- Log all API calls

### Data Privacy
- Encrypt sensitive data
- Implement data retention policies
- Comply with privacy regulations

## 🎉 Success Indicators

You'll know everything is working when you see:

✅ **Real SMS messages** appearing in the dashboard table  
✅ **MPESA transactions** being automatically parsed  
✅ **Real-time updates** every 30 seconds  
✅ **Statistics updating** automatically  
✅ **"Fetch New SMS" button** working  
✅ **No error messages** in the console  

## 🚀 Next Steps

1. **Monitor Performance**: Watch dashboard for real-time updates
2. **Customize Parsing**: Add new MPESA patterns as needed
3. **Scale Up**: Add more SMS sources if required
4. **Integrate**: Connect with other systems via webhooks
5. **Analyze**: Use the data for business insights

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review Django server logs
3. Test with the provided test scripts
4. Verify your SMSMobileAPI account status

---

**🎯 Your Django SMS Dashboard is now ready to fetch and display real SMS messages in real-time!**

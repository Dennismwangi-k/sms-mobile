# 🚀 Quick Start Guide

Get your SMS Webhook Dashboard running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## ⚡ Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Setup Script
```bash
python setup.py
```

This will:
- ✅ Create environment configuration
- ✅ Set up the database
- ✅ Create admin user (optional)
- ✅ Collect static files

### 3. Start the Server
```bash
python manage.py runserver
```

### 4. Open Your Browser
- **Dashboard**: http://localhost:8000/
- **Admin**: http://localhost:8000/admin/
- **API**: http://localhost:8000/api/

## 🔧 Manual Setup (Alternative)

If you prefer manual setup:

### 1. Create Environment File
```bash
cp env.example .env
# Edit .env with your settings
```

### 2. Setup Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Admin User
```bash
python manage.py createsuperuser
```

### 4. Start Server
```bash
python manage.py runserver
```

## 🧪 Test the Webhook

### 1. Test with Sample Data
```bash
python test_webhook.py
```

### 2. Manual Test
Send a POST request to `http://localhost:8000/webhook/sms/` with:

```json
{
  "date": "2025-01-20",
  "hour": "10:15:00",
  "time_received": "2025-01-20 10:14:50",
  "message": "ABC12345 Confirmed. You have received Ksh 5,000.00 from John Doe +254712345678 on 20/01/25 at 10:15 AM",
  "number": "MPESA",
  "guid": "test_guid_001"
}
```

## 📱 Configure SMSMobileAPI

1. **Get API Key**: Download SMSMobileAPI app and create account
2. **Set Webhook URL**: Configure `http://localhost:8000/webhook/sms/` in SMSMobileAPI dashboard
3. **Test**: Send an SMS to your connected phone

## 🎯 What You'll See

- **Dashboard**: Real-time statistics and recent activity
- **SMS Messages**: All incoming SMS with filtering and search
- **MPESA Transactions**: Parsed financial transactions
- **Admin Panel**: Manage data and monitor webhook logs

## 🚨 Troubleshooting

### Server Won't Start
- Check Python version: `python --version`
- Verify dependencies: `pip list | grep Django`
- Check port availability: `lsof -i :8000`

### Database Errors
- Run: `python manage.py migrate`
- Check: `python manage.py showmigrations`

### Webhook Not Working
- Verify URL: `http://localhost:8000/webhook/sms/`
- Check logs in admin panel
- Test with `python test_webhook.py`

## 📚 Next Steps

- Read the full [README.md](README.md)
- Customize the MPESA parser for your needs
- Deploy to production server
- Set up monitoring and alerts

## 🆘 Need Help?

- Check the [README.md](README.md) for detailed documentation
- Review Django logs in the admin panel
- Test individual components step by step

---

**Happy SMS Processing! 🎉**

# SMS Webhook Dashboard

A modern Django web application that receives SMS messages via webhooks from SMSMobileAPI and automatically parses MPESA transactions. Built with Django, Django REST Framework, and a beautiful Tailwind CSS interface.

## Features

- **Real-time SMS Reception**: Webhook endpoint to receive SMS messages from SMSMobileAPI
- **Automatic MPESA Parsing**: Intelligent parsing of MPESA transaction SMS messages
- **Beautiful Dashboard**: Modern, responsive web interface with real-time statistics
- **REST API**: Full API endpoints for integration with other systems
- **Advanced Filtering**: Search and filter SMS messages and MPESA transactions
- **Admin Interface**: Django admin for managing data and monitoring webhook logs
- **Comprehensive Logging**: Track all webhook requests and processing results

## Screenshots

The application features a modern dashboard with:
- Statistics cards showing total SMS, MPESA transactions, and processing status
- Recent activity feeds for both SMS messages and MPESA transactions
- MPESA transaction summary with amounts by direction
- Webhook configuration information

## Installation

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smswebhook
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Dashboard: http://localhost:8000/
   - Admin: http://localhost:8000/admin/
   - API: http://localhost:8000/api/

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# SMSMobileAPI Configuration
SMSMOBILE_API_KEY=your-smsmobile-api-key-here
SMSMOBILE_BASE_URL=https://api.smsmobileapi.com

# CORS Settings (if needed)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### SMSMobileAPI Setup

1. Download the SMSMobileAPI mobile app from [Google Play](https://play.google.com/store/apps/details?id=com.smsmobileapi.app) or [App Store](https://apps.apple.com/app/smsmobileapi/id1234567890)
2. Create an account and get your API key
3. Configure the webhook URL in the SMSMobileAPI dashboard:
   ```
   https://yourdomain.com/webhook/sms/
   ```

## Usage

### Webhook Endpoint

The application automatically receives SMS messages at:
```
POST /webhook/sms/
```

**Expected Payload:**
```json
{
  "date": "2025-01-20",
  "hour": "10:15:00",
  "time_received": "2025-01-20 10:14:50",
  "message": "Hello, this is a test.",
  "number": "+123456789",
  "guid": "abcde12345"
}
```

### MPESA Parsing

The application automatically detects and parses MPESA SMS messages, extracting:
- Transaction code
- Amount
- Direction (received/sent/paid)
- Party name and phone number
- Transaction date and time
- Parsing confidence score

### API Endpoints

#### SMS Messages
- `GET /api/sms/` - List all SMS messages
- `GET /api/sms/{id}/` - Get specific SMS message
- `POST /api/sms/{id}/mark_processed/` - Mark SMS as processed
- `POST /api/sms/{id}/mark_failed/` - Mark SMS as failed

#### MPESA Transactions
- `GET /api/mpesa/` - List all MPESA transactions
- `GET /api/mpesa/{id}/` - Get specific MPESA transaction
- `GET /api/mpesa/statistics/` - Get MPESA statistics

#### Query Parameters
- `search` - Search by text content
- `status` - Filter by SMS status
- `direction` - Filter by direction
- `valid_only` - Show only valid MPESA transactions

## Project Structure

```
smswebhook/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── env.example              # Environment variables template
├── smswebhook/              # Main Django project
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── sms_webhook/             # Main Django app
│   ├── __init__.py
│   ├── admin.py             # Admin interface configuration
│   ├── apps.py              # App configuration
│   ├── models.py            # Database models
│   ├── views.py             # View logic
│   ├── urls.py              # App URL configuration
│   ├── serializers.py       # REST API serializers
│   └── mpesa_parser.py      # MPESA parsing logic
├── templates/                # HTML templates
│   ├── base.html            # Base template
│   └── sms_webhook/         # App-specific templates
│       ├── dashboard.html    # Main dashboard
│       ├── sms_list.html    # SMS messages list
│       └── mpesa_list.html  # MPESA transactions list
└── static/                   # Static files (CSS, JS, images)
```

## Models

### SMSMessage
Stores incoming SMS messages with:
- Message content and metadata
- Processing status and notes
- Timestamps and direction

### MPESATransaction
Stores parsed MPESA transactions with:
- Transaction details (amount, code, direction)
- Party information (name, phone)
- Parsing confidence and errors

### WebhookLog
Tracks all webhook requests for debugging:
- Request/response details
- Processing time and errors
- IP addresses and headers

## Customization

### Adding New SMS Providers

To support additional SMS providers beyond MPESA:

1. Create a new parser class in `sms_webhook/parsers/`
2. Implement the parsing logic
3. Update the webhook view to use the new parser
4. Add provider-specific models if needed

### Styling

The application uses Tailwind CSS for styling. Customize the appearance by:
- Modifying the base template (`templates/base.html`)
- Adding custom CSS classes
- Updating the Tailwind configuration

### API Extensions

Extend the REST API by:
- Adding new serializers
- Creating additional viewset actions
- Implementing custom endpoints

## Deployment

### Production Considerations

1. **Security**
   - Set `DEBUG=False`
   - Use strong `SECRET_KEY`
   - Configure `ALLOWED_HOSTS`
   - Enable HTTPS

2. **Database**
   - Use PostgreSQL or MySQL for production
   - Configure database connection pooling
   - Set up regular backups

3. **Web Server**
   - Use Gunicorn or uWSGI
   - Configure Nginx as reverse proxy
   - Set up SSL certificates

4. **Monitoring**
   - Configure logging to external services
   - Set up health checks
   - Monitor webhook performance

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "smswebhook.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## Troubleshooting

### Common Issues

1. **Webhook not receiving messages**
   - Check webhook URL configuration in SMSMobileAPI
   - Verify server is accessible from internet
   - Check webhook logs in admin interface

2. **MPESA parsing errors**
   - Review SMS message format
   - Check parsing confidence scores
   - Examine parsing error logs

3. **Database issues**
   - Run `python manage.py migrate`
   - Check database connection settings
   - Verify model field types

### Debug Mode

Enable debug mode in `.env`:
```env
DEBUG=True
```

This will show detailed error messages and enable the Django debug toolbar.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the SMSMobileAPI documentation
- Review the Django documentation

## Acknowledgments

- [SMSMobileAPI](https://smsmobileapi.com/) for the SMS webhook service
- [Django](https://djangoproject.com/) for the web framework
- [Tailwind CSS](https://tailwindcss.com/) for the styling framework
- [Font Awesome](https://fontawesome.com/) for the icons

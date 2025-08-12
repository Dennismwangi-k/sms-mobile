from django.apps import AppConfig


class SmsWebhookConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sms_webhook'
    verbose_name = 'SMS Webhook'

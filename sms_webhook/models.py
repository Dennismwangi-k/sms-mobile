from django.db import models
from django.utils import timezone
import json


class SMSMessage(models.Model):
    """Model to store incoming SMS messages from webhooks"""
    
    DIRECTION_CHOICES = [
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
    ]
    
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ]
    
    # SMS details
    guid = models.CharField(max_length=100, unique=True, help_text="Unique identifier from SMSMobileAPI")
    number = models.CharField(max_length=20, help_text="Phone number of sender/recipient")
    message = models.TextField(help_text="SMS message content")
    date = models.DateField(help_text="Date when SMS was received")
    hour = models.TimeField(help_text="Hour when SMS was received")
    time_received = models.DateTimeField(help_text="Full timestamp when SMS was received")
    
    # Processing details
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES, default='incoming')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='received')
    processed_at = models.DateTimeField(null=True, blank=True)
    processing_notes = models.TextField(blank=True)
    
    # Metadata
    raw_payload = models.JSONField(default=dict, help_text="Original webhook payload")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-time_received']
        verbose_name = 'SMS Message'
        verbose_name_plural = 'SMS Messages'
        indexes = [
            models.Index(fields=['number']),
            models.Index(fields=['time_received']),
            models.Index(fields=['status']),
            models.Index(fields=['guid']),
        ]
    
    def __str__(self):
        return f"SMS from {self.number} at {self.time_received}"
    
    def mark_as_processed(self, notes=""):
        """Mark SMS as processed"""
        self.status = 'processed'
        self.processed_at = timezone.now()
        self.processing_notes = notes
        self.save()
    
    def mark_as_failed(self, notes=""):
        """Mark SMS as failed"""
        self.status = 'failed'
        self.processed_at = timezone.now()
        self.processing_notes = notes
        self.save()


class MPESATransaction(models.Model):
    """Model to store parsed MPESA transactions"""
    
    DIRECTION_CHOICES = [
        ('received', 'Received'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
    ]
    
    # MPESA transaction details
    sms_message = models.ForeignKey(SMSMessage, on_delete=models.CASCADE, related_name='mpesa_transactions')
    provider = models.CharField(max_length=20, default='MPESA')
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    tx_code = models.CharField(max_length=20, blank=True, help_text="MPESA transaction code")
    
    # Transaction timing
    tx_date = models.CharField(max_length=20, blank=True, help_text="Transaction date from SMS")
    tx_time = models.CharField(max_length=20, blank=True, help_text="Transaction time from SMS")
    tx_datetime_local = models.DateTimeField(null=True, blank=True, help_text="Combined transaction datetime")
    
    # Parsing metadata
    parsing_confidence = models.FloatField(default=0.0, help_text="Confidence score of parsing (0-1)")
    parsing_errors = models.JSONField(default=list, help_text="List of parsing errors if any")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-tx_datetime_local', '-created_at']
        verbose_name = 'MPESA Transaction'
        verbose_name_plural = 'MPESA Transactions'
        indexes = [
            models.Index(fields=['tx_code']),
            models.Index(fields=['amount']),
            models.Index(fields=['direction']),
            models.Index(fields=['tx_datetime_local']),
        ]
    
    def __str__(self):
        direction_text = self.direction.title()
        amount_text = f"Ksh {self.amount}" if self.amount else "Unknown amount"
        return f"{direction_text} {amount_text} - {self.name or 'Unknown'}"
    
    @property
    def formatted_amount(self):
        """Return formatted amount with currency"""
        if self.amount:
            return f"Ksh {self.amount:,.2f}"
        return "Unknown"
    
    @property
    def is_valid(self):
        """Check if transaction has essential data"""
        return bool(self.tx_code and self.amount and self.direction)


class WebhookLog(models.Model):
    """Model to log webhook requests for debugging"""
    
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('error', 'Error'),
        ('invalid', 'Invalid'),
    ]
    
    endpoint = models.CharField(max_length=200, help_text="Webhook endpoint called")
    method = models.CharField(max_length=10, default='POST')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    status_code = models.IntegerField()
    
    # Request details
    headers = models.JSONField(default=dict)
    body = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Response details
    response_body = models.TextField(blank=True)
    processing_time = models.FloatField(null=True, blank=True, help_text="Processing time in seconds")
    
    # Error details
    error_message = models.TextField(blank=True)
    stack_trace = models.TextField(blank=True)
    
    # Timestamps
    received_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-received_at']
        verbose_name = 'Webhook Log'
        verbose_name_plural = 'Webhook Logs'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['received_at']),
            models.Index(fields=['endpoint']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status} ({self.status_code})"

"""
Serializers for SMS Webhook application
"""

from rest_framework import serializers
from .models import SMSMessage, MPESATransaction, WebhookLog


class SMSMessageSerializer(serializers.ModelSerializer):
    """Serializer for SMS messages"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    direction_display = serializers.CharField(source='get_direction_display', read_only=True)
    time_received_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = SMSMessage
        fields = [
            'id', 'guid', 'number', 'message', 'date', 'hour', 'time_received',
            'direction', 'direction_display', 'status', 'status_display',
            'processed_at', 'processing_notes', 'created_at', 'updated_at',
            'time_received_formatted'
        ]
        read_only_fields = ['id', 'guid', 'created_at', 'updated_at']
    
    def get_time_received_formatted(self, obj):
        """Format time_received for display"""
        if obj.time_received:
            return obj.time_received.strftime('%Y-%m-%d %H:%M:%S')
        return None


class MPESATransactionSerializer(serializers.ModelSerializer):
    """Serializer for MPESA transactions"""
    
    direction_display = serializers.CharField(source='get_direction_display', read_only=True)
    formatted_amount = serializers.CharField(source='formatted_amount', read_only=True)
    is_valid = serializers.BooleanField(source='is_valid', read_only=True)
    tx_datetime_formatted = serializers.SerializerMethodField()
    
    # Related SMS message data
    sms_number = serializers.CharField(source='sms_message.number', read_only=True)
    sms_message_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = MPESATransaction
        fields = [
            'id', 'sms_message', 'sms_number', 'sms_message_preview',
            'provider', 'direction', 'direction_display', 'amount', 'formatted_amount',
            'name', 'phone', 'tx_code', 'tx_date', 'tx_time', 'tx_datetime_local',
            'tx_datetime_formatted', 'parsing_confidence', 'parsing_errors',
            'is_valid', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_tx_datetime_formatted(self, obj):
        """Format tx_datetime_local for display"""
        if obj.tx_datetime_local:
            return obj.tx_datetime_local.strftime('%Y-%m-%d %H:%M:%S')
        return None
    
    def get_sms_message_preview(self, obj):
        """Get preview of SMS message"""
        if obj.sms_message and obj.sms_message.message:
            message = obj.sms_message.message
            if len(message) > 100:
                return f"{message[:100]}..."
            return message
        return ""


class WebhookLogSerializer(serializers.ModelSerializer):
    """Serializer for webhook logs"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    received_at_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = WebhookLog
        fields = [
            'id', 'endpoint', 'method', 'status', 'status_display', 'status_code',
            'headers', 'body', 'ip_address', 'response_body', 'processing_time',
            'error_message', 'stack_trace', 'received_at', 'received_at_formatted'
        ]
        read_only_fields = ['id', 'received_at']
    
    def get_received_at_formatted(self, obj):
        """Format received_at for display"""
        if obj.received_at:
            return obj.received_at.strftime('%Y-%m-%d %H:%M:%S')
        return None


class MPESAStatisticsSerializer(serializers.Serializer):
    """Serializer for MPESA statistics"""
    
    total_transactions = serializers.IntegerField()
    valid_transactions = serializers.IntegerField()
    amount_totals = serializers.DictField(
        child=serializers.DecimalField(max_digits=15, decimal_places=2)
    )


class WebhookPayloadSerializer(serializers.Serializer):
    """Serializer for validating webhook payloads"""
    
    date = serializers.DateField()
    hour = serializers.TimeField()
    time_received = serializers.DateTimeField()
    message = serializers.CharField()
    number = serializers.CharField()
    guid = serializers.CharField()
    
    def validate_date(self, value):
        """Validate date format"""
        if not value:
            raise serializers.ValidationError("Date is required")
        return value
    
    def validate_guid(self, value):
        """Validate GUID format"""
        if not value or len(value) < 5:
            raise serializers.ValidationError("GUID must be at least 5 characters")
        return value

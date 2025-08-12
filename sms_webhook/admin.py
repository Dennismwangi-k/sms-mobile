from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import SMSMessage, MPESATransaction, WebhookLog


@admin.register(SMSMessage)
class SMSMessageAdmin(admin.ModelAdmin):
    list_display = ['number', 'short_message', 'time_received', 'status', 'direction', 'created_at']
    list_filter = ['status', 'direction', 'date', 'created_at']
    search_fields = ['number', 'message', 'guid']
    readonly_fields = ['guid', 'created_at', 'updated_at']
    date_hierarchy = 'time_received'
    
    fieldsets = (
        ('SMS Details', {
            'fields': ('guid', 'number', 'message', 'date', 'hour', 'time_received')
        }),
        ('Processing', {
            'fields': ('direction', 'status', 'processed_at', 'processing_notes')
        }),
        ('Metadata', {
            'fields': ('raw_payload', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def short_message(self, obj):
        """Display truncated message"""
        if len(obj.message) > 50:
            return f"{obj.message[:50]}..."
        return obj.message
    short_message.short_description = 'Message'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(MPESATransaction)
class MPESATransactionAdmin(admin.ModelAdmin):
    list_display = ['tx_code', 'direction', 'amount', 'name', 'phone', 'tx_datetime_local', 'is_valid']
    list_filter = ['direction', 'provider', 'created_at', 'tx_datetime_local']
    search_fields = ['tx_code', 'name', 'phone', 'sms_message__message']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'tx_datetime_local'
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('sms_message', 'provider', 'direction', 'amount', 'tx_code')
        }),
        ('Party Information', {
            'fields': ('name', 'phone')
        }),
        ('Timing', {
            'fields': ('tx_date', 'tx_time', 'tx_datetime_local')
        }),
        ('Parsing', {
            'fields': ('parsing_confidence', 'parsing_errors')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_valid(self, obj):
        """Display if transaction is valid"""
        if obj.is_valid:
            return format_html('<span style="color: green;">✓ Valid</span>')
        return format_html('<span style="color: red;">✗ Invalid</span>')
    is_valid.boolean = True
    is_valid.short_description = 'Valid'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sms_message')


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = ['endpoint', 'method', 'status', 'status_code', 'ip_address', 'received_at']
    list_filter = ['status', 'method', 'endpoint', 'received_at']
    search_fields = ['endpoint', 'error_message']
    readonly_fields = ['received_at']
    date_hierarchy = 'received_at'
    
    fieldsets = (
        ('Request Details', {
            'fields': ('endpoint', 'method', 'status', 'status_code')
        }),
        ('Request Data', {
            'fields': ('headers', 'body', 'ip_address'),
            'classes': ('collapse',)
        }),
        ('Response', {
            'fields': ('response_body', 'processing_time'),
            'classes': ('collapse',)
        }),
        ('Errors', {
            'fields': ('error_message', 'stack_trace'),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('received_at',)
        }),
    )
    
    def has_add_permission(self, request):
        """Webhook logs are created automatically"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Webhook logs should not be modified"""
        return False

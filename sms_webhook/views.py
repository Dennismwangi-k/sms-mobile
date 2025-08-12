"""
Views for SMS Webhook application
"""

import json
import time
import logging
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from .models import SMSMessage, MPESATransaction, WebhookLog
from .mpesa_parser import mpesa_parser
from .serializers import SMSMessageSerializer, MPESATransactionSerializer

logger = logging.getLogger(__name__)


class WebhookView(View):
    """Handle incoming SMS webhooks from SMSMobileAPI"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        """Process incoming webhook"""
        start_time = time.time()
        
        # Log the webhook request
        webhook_log = WebhookLog.objects.create(
            endpoint=request.path,
            method=request.method,
            status='success',
            status_code=200,
            headers=dict(request.headers),
            body=request.body.decode('utf-8', errors='ignore'),
            ip_address=self._get_client_ip(request)
        )
        
        try:
            # Parse the webhook payload
            payload = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['date', 'hour', 'time_received', 'message', 'number', 'guid']
            missing_fields = [field for field in required_fields if field not in payload]
            
            if missing_fields:
                error_msg = f"Missing required fields: {missing_fields}"
                logger.error(error_msg)
                webhook_log.status = 'invalid'
                webhook_log.status_code = 400
                webhook_log.error_message = error_msg
                webhook_log.save()
                return JsonResponse({'error': error_msg}, status=400)
            
            # Create SMS message record
            sms_message = SMSMessage.objects.create(
                guid=payload['guid'],
                number=payload['number'],
                message=payload['message'],
                date=datetime.strptime(payload['date'], '%Y-%m-%d').date(),
                hour=datetime.strptime(payload['hour'], '%H:%M:%S').time(),
                time_received=datetime.strptime(payload['time_received'], '%Y-%m-%d %H:%M:%S'),
                raw_payload=payload
            )
            
            # Try to parse as MPESA transaction
            if mpesa_parser.is_mpesa_message(payload['message'], payload['number']):
                parsed_data = mpesa_parser.parse(payload['message'], payload['number'])
                
                if parsed_data['direction']:
                    MPESATransaction.objects.create(
                        sms_message=sms_message,
                        provider=parsed_data['provider'],
                        direction=parsed_data['direction'],
                        amount=parsed_data['amount'],
                        name=parsed_data['name'],
                        phone=parsed_data['phone'],
                        tx_code=parsed_data['tx_code'],
                        tx_date=parsed_data['date'],
                        tx_time=parsed_data['time'],
                        tx_datetime_local=parsed_data['tx_datetime_local'],
                        parsing_confidence=parsed_data['parsing_confidence'],
                        parsing_errors=parsed_data['parsing_errors']
                    )
                    
                    # Mark SMS as processed
                    sms_message.mark_as_processed("Successfully parsed as MPESA transaction")
                else:
                    sms_message.mark_as_failed("Failed to parse MPESA transaction")
            else:
                # Mark SMS as processed (not MPESA)
                sms_message.mark_as_processed("SMS received (not MPESA)")
            
            # Update webhook log
            processing_time = time.time() - start_time
            webhook_log.processing_time = processing_time
            webhook_log.response_body = json.dumps({'status': 'success', 'guid': payload['guid']})
            webhook_log.save()
            
            logger.info(f"Webhook processed successfully: {payload['guid']}")
            return JsonResponse({'status': 'success', 'guid': payload['guid']})
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON payload: {str(e)}"
            logger.error(error_msg)
            webhook_log.status = 'error'
            webhook_log.status_code = 400
            webhook_log.error_message = error_msg
            webhook_log.save()
            return JsonResponse({'error': error_msg}, status=400)
            
        except Exception as e:
            error_msg = f"Error processing webhook: {str(e)}"
            logger.error(error_msg, exc_info=True)
            webhook_log.status = 'error'
            webhook_log.status_code = 500
            webhook_log.error_message = error_msg
            webhook_log.save()
            return JsonResponse({'error': 'Internal server error'}, status=500)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@method_decorator(csrf_exempt, name='dispatch')
class FetchSMSView(View):
    """API endpoint to fetch SMS messages from SMSMobileAPI"""
    
    def post(self, request):
        """Fetch SMS messages from SMSMobileAPI"""
        try:
            from .sms_fetcher import sms_fetcher
            
            # Fetch all available SMS messages
            new_messages = sms_fetcher.fetch_and_store_sms(only_unread=False)
            
            return JsonResponse({
                'success': True,
                'count': len(new_messages),
                'message': f'Successfully fetched {len(new_messages)} new SMS messages'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class DashboardDataView(View):
    """API endpoint to get dashboard data for real-time updates"""
    
    def get(self, request):
        """Get dashboard statistics for real-time updates"""
        try:
            # Get statistics
            total_sms = SMSMessage.objects.count()
            total_mpesa = MPESATransaction.objects.count()
            unprocessed_sms = SMSMessage.objects.filter(status='received').count()
            
            # Get MPESA statistics by direction
            mpesa_stats = {}
            for direction in ['received', 'sent', 'paid']:
                count = MPESATransaction.objects.filter(direction=direction).count()
                total_amount = MPESATransaction.objects.filter(
                    direction=direction, 
                    amount__isnull=False
                ).aggregate(total=Sum('amount'))['total'] or 0
                mpesa_stats[direction] = {'count': count, 'total_amount': total_amount}
            
            return JsonResponse({
                'success': True,
                'total_sms': total_sms,
                'total_mpesa': total_mpesa,
                'unprocessed_sms': unprocessed_sms,
                'mpesa_stats': mpesa_stats,
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AutoFetchSMSView(View):
    """API endpoint to automatically fetch new SMS messages"""
    
    def post(self, request):
        """Automatically fetch new SMS messages"""
        try:
            from .sms_fetcher import sms_fetcher
            
            # Get the latest timestamp from our database
            latest_timestamp = sms_fetcher.get_latest_timestamp()
            
            # Fetch only messages newer than our latest
            new_messages = sms_fetcher.fetch_and_store_sms(
                only_unread=False, 
                after_ts=latest_timestamp
            )
            
            return JsonResponse({
                'success': True,
                'count': len(new_messages),
                'new_messages': len(new_messages),
                'message': f'Found {len(new_messages)} new SMS messages'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SMSTableView(View):
    """API endpoint to get SMS table data for real-time updates"""
    
    def get(self, request):
        """Get SMS table data for the current page"""
        try:
            from django.core.paginator import Paginator
            
            # Get page number from request
            page_number = request.GET.get('page', 1)
            
            # Get SMS messages
            sms_list = SMSMessage.objects.all().order_by('-time_received')
            paginator = Paginator(sms_list, 20)  # 20 messages per page
            
            try:
                page_obj = paginator.page(page_number)
            except:
                page_obj = paginator.page(1)
            
            # Prepare SMS data for the table
            sms_messages = []
            for sms in page_obj:
                sms_messages.append({
                    'id': sms.id,
                    'guid': sms.guid,
                    'number': sms.number,
                    'message': sms.message,
                    'status': sms.status,
                    'direction': sms.direction,
                    'time_received': sms.time_received.isoformat(),
                    'get_status_display': sms.get_status_display(),
                    'get_direction_display': sms.get_direction_display(),
                })
            
            # Prepare pagination data
            pagination = {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'start_index': page_obj.start_index(),
                'end_index': page_obj.end_index(),
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
            }
            
            return JsonResponse({
                'success': True,
                'sms_messages': sms_messages,
                'pagination': pagination,
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class DashboardView(View):
    """Main dashboard view"""
    
    def get(self, request):
        """Display dashboard with SMS and MPESA data"""
        # Get recent SMS messages
        recent_sms = SMSMessage.objects.select_related().order_by('-time_received')[:10]
        
        # Get recent MPESA transactions
        recent_mpesa = MPESATransaction.objects.select_related('sms_message').order_by('-created_at')[:10]
        
        # Get all SMS messages for the table (paginated)
        from django.core.paginator import Paginator
        sms_list = SMSMessage.objects.all().order_by('-time_received')
        paginator = Paginator(sms_list, 20)  # Show 20 messages per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get statistics
        total_sms = SMSMessage.objects.count()
        total_mpesa = MPESATransaction.objects.count()
        unprocessed_sms = SMSMessage.objects.filter(status='received').count()
        
        # Get MPESA statistics by direction
        mpesa_stats = {}
        for direction in ['received', 'sent', 'paid']:
            count = MPESATransaction.objects.filter(direction=direction).count()
            total_amount = MPESATransaction.objects.filter(
                direction=direction, 
                amount__isnull=False
            ).aggregate(total=Sum('amount'))['total'] or 0
            mpesa_stats[direction] = {'count': count, 'total_amount': total_amount}
        
        context = {
            'recent_sms': recent_sms,
            'recent_mpesa': recent_mpesa,
            'page_obj': page_obj,  # For the SMS table
            'total_sms': total_sms,
            'total_mpesa': total_mpesa,
            'unprocessed_sms': unprocessed_sms,
            'mpesa_stats': mpesa_stats,
        }
        
        return render(request, 'sms_webhook/dashboard.html', context)


class SMSListView(View):
    """List SMS messages with filtering and pagination"""
    
    def get(self, request):
        """Display paginated list of SMS messages"""
        # Get filter parameters
        search = request.GET.get('search', '')
        status_filter = request.GET.get('status', '')
        direction_filter = request.GET.get('direction', '')
        
        # Build queryset
        queryset = SMSMessage.objects.all()
        
        if search:
            queryset = queryset.filter(
                Q(number__icontains=search) |
                Q(message__icontains=search) |
                Q(guid__icontains=search)
            )
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if direction_filter:
            queryset = queryset.filter(direction=direction_filter)
        
        # Pagination
        paginator = Paginator(queryset.order_by('-time_received'), 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'search': search,
            'status_filter': status_filter,
            'direction_filter': direction_filter,
            'status_choices': SMSMessage.STATUS_CHOICES,
            'direction_choices': SMSMessage.DIRECTION_CHOICES,
        }
        
        return render(request, 'sms_webhook/sms_list.html', context)


class MPESAListView(View):
    """List MPESA transactions with filtering and pagination"""
    
    def get(self, request):
        """Display paginated list of MPESA transactions"""
        # Get filter parameters
        search = request.GET.get('search', '')
        direction_filter = request.GET.get('direction', '')
        valid_only = request.GET.get('valid_only', '')
        
        # Build queryset
        queryset = MPESATransaction.objects.select_related('sms_message')
        
        if search:
            queryset = queryset.filter(
                Q(tx_code__icontains=search) |
                Q(name__icontains=search) |
                Q(phone__icontains=search) |
                Q(sms_message__message__icontains=search)
            )
        
        if direction_filter:
            queryset = queryset.filter(direction=direction_filter)
        
        if valid_only:
            queryset = queryset.filter(amount__isnull=False, tx_code__isnull=False)
        
        # Pagination
        paginator = Paginator(queryset.order_by('-tx_datetime_local', '-created_at'), 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'search': search,
            'direction_filter': direction_filter,
            'valid_only': valid_only,
            'direction_choices': MPESATransaction.DIRECTION_CHOICES,
        }
        
        return render(request, 'sms_webhook/mpesa_list.html', context)


# REST API Viewsets
class SMSMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """API viewset for SMS messages"""
    queryset = SMSMessage.objects.all().order_by('-time_received')
    serializer_class = SMSMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = SMSMessage.objects.all()
        
        # Filter by status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by direction
        direction = self.request.query_params.get('direction', None)
        if direction:
            queryset = queryset.filter(direction=direction)
        
        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(number__icontains=search) |
                Q(message__icontains=search) |
                Q(guid__icontains=search)
            )
        
        return queryset.order_by('-time_received')
    
    @action(detail=True, methods=['post'])
    def mark_processed(self, request, pk=None):
        """Mark SMS as processed"""
        sms = self.get_object()
        notes = request.data.get('notes', '')
        sms.mark_as_processed(notes)
        return Response({'status': 'success'})
    
    @action(detail=True, methods=['post'])
    def mark_failed(self, request, pk=None):
        """Mark SMS as failed"""
        sms = self.get_object()
        notes = request.data.get('notes', '')
        sms.mark_as_failed(notes)
        return Response({'status': 'success'})


class MPESATransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """API viewset for MPESA transactions"""
    queryset = MPESATransaction.objects.select_related('sms_message').order_by('-created_at')
    serializer_class = MPESATransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = MPESATransaction.objects.select_related('sms_message')
        
        # Filter by direction
        direction = self.request.query_params.get('direction', None)
        if direction:
            queryset = queryset.filter(direction=direction)
        
        # Filter by validity
        valid_only = self.request.query_params.get('valid_only', None)
        if valid_only:
            queryset = queryset.filter(amount__isnull=False, tx_code__isnull=False)
        
        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(tx_code__icontains=search) |
                Q(name__icontains=search) |
                Q(phone__icontains=search) |
                Q(sms_message__message__icontains=search)
            )
        
        return queryset.order_by('-tx_datetime_local', '-created_at')
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get MPESA transaction statistics"""
        total = MPESATransaction.objects.count()
        valid = MPESATransaction.objects.filter(amount__isnull=False, tx_code__isnull=False).count()
        
        # Amount totals by direction
        amount_totals = {}
        for direction in ['received', 'sent', 'paid']:
            total_amount = MPESATransaction.objects.filter(
                direction=direction, 
                amount__isnull=False
            ).aggregate(total=Sum('amount'))['total'] or 0
            amount_totals[direction] = total_amount
        
        return Response({
            'total_transactions': total,
            'valid_transactions': valid,
            'amount_totals': amount_totals,
        })

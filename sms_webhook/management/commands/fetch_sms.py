"""
Django management command to fetch SMS messages from SMSMobileAPI
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from sms_webhook.sms_fetcher import sms_fetcher


class Command(BaseCommand):
    help = 'Fetch SMS messages from SMSMobileAPI and store them in the database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--unread-only',
            action='store_true',
            help='Fetch only unread messages',
        )
        parser.add_argument(
            '--device-id',
            type=str,
            help='Specific device ID to fetch from',
        )
        parser.add_argument(
            '--hours-back',
            type=int,
            default=24,
            help='Number of hours back to sync (default: 24)',
        )
        parser.add_argument(
            '--sync-recent',
            action='store_true',
            help='Sync recent messages from the last N hours',
        )
    
    def handle(self, *args, **options):
        try:
            if options['sync_recent']:
                self.stdout.write(f"Syncing recent messages from the last {options['hours_back']} hours...")
                messages = sms_fetcher.sync_recent_messages(hours_back=options['hours_back'])
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully synced {len(messages)} messages')
                )
            else:
                self.stdout.write("Fetching SMS messages...")
                messages = sms_fetcher.fetch_and_store_sms(
                    only_unread=options['unread_only'],
                    device_id=options['device_id']
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully fetched and stored {len(messages)} messages')
                )
                
        except ValueError as e:
            raise CommandError(f"Configuration error: {e}")
        except Exception as e:
            raise CommandError(f"Error fetching SMS: {e}")

from django.core.management.base import BaseCommand
from tracking.models import BlockedIP

class Command(BaseCommand):
    help = 'Block an IP address'

    def add_arguments(self, parser):
        parser.add_argument('ip_address', type=str)

    def handle(self, *args, **options):
        ip = options['ip_address']
        BlockedIP.objects.get_or_create(ip_address=ip)
        self.stdout.write(
            self.style.SUCCESS(f'Successfully blocked IP: {ip}')
        )
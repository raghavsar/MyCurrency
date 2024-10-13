from django.core.management.base import BaseCommand
from fx_rates.providers.providers import get_active_provider
from django.conf import settings

class Command(BaseCommand):
    help = "Load all currencies from the active provider and store them in the database."

    def handle(self, *args, **kwargs):
        # Fetch the active provider dynamically
        provider = get_active_provider()

        try:
            provider.store_currencies()
            self.stdout.write(self.style.SUCCESS('Successfully loaded and stored all currencies.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading currencies: {e}"))

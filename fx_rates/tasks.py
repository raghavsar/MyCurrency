from celery import shared_task
from .models import Currency, CurrencyExchangeRate
from .utils import get_exchange_rate_data
from django.core.management import call_command
import logging
logger = logging.getLogger(__name__)


@shared_task
def fetch_and_store_currencies():
    """
    Fetches all currencies data from the provider and stores it in the database.
    """

    call_command('fetch_currencies')
    logger.info("All currencies data fetched and stored successfully.")


@shared_task
def load_historical_data(start_date, end_date, batch_size=1000):
    """
    Loads historical exchange rate data asynchronously.

    Args:
        start_date: The start date for the data to load.
        end_date: The end date for the data to load.
        batch_size: The number of exchange rates to process in each batch.
    """

    currencies = Currency.objects.all()
    total_batches = (end_date - start_date).days // batch_size + 1

    for i in range(total_batches):
        batch_start_date = start_date + i * batch_size
        batch_end_date = batch_start_date + batch_size - 1

        for source_currency in currencies:
            for target_currency in currencies:
                if source_currency != target_currency:
                    for valuation_date in range(batch_start_date, batch_end_date + 1):
                        rate = get_exchange_rate_data(source_currency.code, target_currency.code, valuation_date)
                        if rate:
                            CurrencyExchangeRate.objects.create(
                                source_currency=source_currency,
                                exchanged_currency=target_currency,
                                valuation_date=valuation_date,
                                rate_value=rate.rate_value
                            )

    logger.info(f"Historical data loaded for dates {start_date} to {end_date}")
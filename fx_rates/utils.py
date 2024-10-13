from django.conf import settings
from fx_rates.providers.providers import CurrencyBeaconProvider, MockProvider
from django.core.cache import cache
import logging
import asyncio

logger = logging.getLogger(__name__)

def get_exchange_rate_data(source_currency, exchanged_currency, valuation_date):
    cache_key = f"exchange_rate:{source_currency}:{exchanged_currency}:{valuation_date}"
    rate = cache.get(cache_key)

    if rate is None:
        providers = settings.EXCHANGE_RATE_PROVIDERS
        for provider_name, provider_config in providers.items():
            if provider_config['active']:
                try:
                    provider = eval(provider_name)(**provider_config['params'])
                    rate =  provider.get_exchange_rate_data(
                        source_currency, exchanged_currency, valuation_date)
                    if rate:
                        cache.set(cache_key, rate, 60 * 60)  # Cache for 1 hour
                        return rate
                except Exception as e:
                    logger.error(f"Error in provider: {e}")

    return rate

def get_exchange_rate_data_timeseries(source_currency, date_from, date_to):
    providers = settings.EXCHANGE_RATE_PROVIDERS
    for provider_name, provider_config in providers.items():
        if provider_config['active']:
            try:
                provider = eval(provider_name)(**provider_config['params'])
                rate =  provider.get_exchange_rate_data_timeseries(
                    source_currency, date_from, date_to)
                if rate:
                    return rate
            except Exception as e:
                logger.error(f"Error in provider: {e}")

    return None

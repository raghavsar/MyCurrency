import requests
from django.conf import settings
from fx_rates.models import CurrencyExchangeRate, Currency
import random
from datetime import date
import logging
import os , sys
from datetime import datetime, timedelta
from fx_rates.data import currencies
logger = logging.getLogger(__name__)

class CurrencyBeaconProvider:
    def __init__(self, base_url,api_key):
        self.base_url = base_url
        self.api_key = api_key

    def get_all_currencies(self):
        url = f"{self.base_url}/currencies?api_key={self.api_key}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            return data['response']
        else:
            raise Exception(f"Failed to fetch currencies. Status code: {response.status_code}")

    def store_currencies(self):
        currencies = self.get_all_currencies()
        for currency_data in currencies:
            Currency.objects.update_or_create(
                code=currency_data['short_code'],
                defaults={
                    'name': currency_data['name'],
                    'symbol': currency_data['symbol'],
                }
            )

    def get_exchange_rate_data_timeseries(self,source_currency, date_from, date_to):

        url = f"{self.base_url}/timeseries?api_key={self.api_key}&base={source_currency}&start_date={date_from}&end_date={date_to}"
        rate = None

        try:
            response = requests.get(url,timeout=10)
            response.raise_for_status()  
            data = response.json()
            return data['response']

        except Exception as e:
            logger.error(f"Error fetching exchange rate from iceAPI: {e}")

        return rate

    def get_exchange_rate_data(self, source_currency, 
                               exchanged_currency, valuation_date):
        api_key = self.api_key
        base_url = "https://api.currencybeacon.com/v1"
        rate = None
        if valuation_date == date.today():
            # Use latest endpoint for today's rates
            url = f"{base_url}/latest?base={source_currency}&symbols={exchanged_currency}&api_key={api_key}"
        else:
            # Use historical endpoint for past dates
            url = f"{base_url}/historical?base={source_currency}&date={valuation_date}&symbols={exchanged_currency}&api_key={api_key}"

        try:
            response = requests.get(url,timeout=10)
            response.raise_for_status()  # Raise an exception for error responses
            data = response.json()

            # Check for successful response based on iceAPI structure
            if "rates" in data and data["rates"]:
                rate_value = data["rates"][exchanged_currency]
                currency_exchange = CurrencyExchangeRate(
                    source_currency=Currency.objects.get(code=source_currency),
                    exchanged_currency=Currency.objects.get(code=exchanged_currency),
                    valuation_date=valuation_date,
                    rate_value=rate_value
                )
                currency_exchange.save()
                return currency_exchange
            else:
                logger.warning(f"iceAPI response for {url} doesn't contain rates")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching exchange rate from iceAPI: {e}")

        return rate

class MockProvider:
    def get_exchange_rate_data(self, source_currency, exchanged_currency, valuation_date):
        # Generate random mock data
        rate_value = round(random.uniform(0.5, 2.5), 6)
        return CurrencyExchangeRate(
            source_currency=Currency.objects.get(code=source_currency),
            exchanged_currency=Currency.objects.get(code=exchanged_currency),
            valuation_date=valuation_date,
            rate_value=rate_value
        )
    
    def get_exchange_rate_data_timeseries(self,source_currency, date_from, date_to):
        date_format = "%Y-%m-%d"
        start_date = datetime.strptime(date_from, date_format)
        end_date = datetime.strptime(date_to, date_format)
        delta = end_date - start_date

          # Add more currencies as needed
        timeseries_data = {}

        for i in range(delta.days + 1):  # Loop through each day in the range
            current_date = (start_date + timedelta(days=i)).strftime(date_format)
            daily_rates = {currency: round(random.uniform(0.5, 3.0), 8) for currency in currencies}  # Generate random rates
            timeseries_data[current_date] = daily_rates

        print(timeseries_data)
        return timeseries_data
    


def get_active_provider():
    providers = settings.EXCHANGE_RATE_PROVIDERS

    if providers['CurrencyBeaconProvider']['active']:
        api_key = providers['CurrencyBeaconProvider']['params'].get('api_key')
        base_url = providers['CurrencyBeaconProvider']['params'].get('base_url')
        return CurrencyBeaconProvider(base_url = base_url,api_key=api_key)
    elif providers['MockProvider']['active']:
        return MockProvider()
    else:
        raise Exception("No active exchange rate provider found.")
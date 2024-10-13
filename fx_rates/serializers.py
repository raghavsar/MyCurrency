from rest_framework import serializers
from .models import Currency, CurrencyExchangeRate

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ('id','code', 'name', 'symbol')

class CurrencyExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyExchangeRate
        fields = ('source_currency', 'exchanged_currency', 'valuation_date', 'rate_value')
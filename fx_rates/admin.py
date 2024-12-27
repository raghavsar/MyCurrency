import numpy
import pandas
import matplotlib.pyplot as plt
from django.contrib import admin
from .models import Currency, CurrencyExchangeRate

class CurrencyAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "name",
        "symbol",
    ]
    search_fields = [
        "code",
        "name",
        "symbol",
    ]

class CurrencyExchangeRateAdmin(admin.ModelAdmin):
    list_display = [
        "source_currency",
        "exchanged_currency",
        "valuation_date",
        "rate_value"]
    
admin.site.register(Currency,CurrencyAdmin)
admin.site.register(CurrencyExchangeRate,CurrencyExchangeRateAdmin)



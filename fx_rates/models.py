from django.db import models


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=20)
    symbol = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class CurrencyExchangeRate(models.Model):
    source_currency = models.ForeignKey(Currency, related_name='source_exchanges', on_delete=models.CASCADE)
    exchanged_currency = models.ForeignKey(Currency, related_name='target_exchanges', on_delete=models.CASCADE)
    valuation_date = models.DateField()
    rate_value = models.DecimalField(max_digits=18, decimal_places=6)

    def __str__(self):
        return f"{self.source_currency} to {self.exchanged_currency} on {self.valuation_date}: {self.rate_value}"
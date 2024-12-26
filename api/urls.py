from django.urls import path, include,
from rest_framework.routers import DefaultRouter
from fx_rates.views import CurrencyViewSet,CurrencyExchangeRateViewSet

app_name = 'mycurrency'

router = DefaultRouter()
router.register(r'currencies', CurrencyViewSet, basename="curreny")
router.register(r'exchange_rates', CurrencyExchangeRateViewSet, basename="currency_exchange")

urlpatterns = [,,,
    path('', include(router.urls)),


]

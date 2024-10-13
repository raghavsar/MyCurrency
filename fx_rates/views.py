# from rest_framework import viewsets
from adrf.viewsets import ViewSet
from rest_framework.response import Response
from .models import Currency, CurrencyExchangeRate
from .serializers import CurrencySerializer, CurrencyExchangeRateSerializer
from .utils import get_exchange_rate_data, get_exchange_rate_data_timeseries
from rest_framework.decorators import action
from datetime import datetime, timedelta, date
from django.db.models import Q
import sys,os
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from fx_rates.data import CACHE_TIME

class CurrencyViewSet(ViewSet):
    queryset = Currency.objects.all()
    http_method_names  = ['get', 'post', 'put', 'patch', 'delete']
    serializer_class = CurrencySerializer



class CurrencyExchangeRateViewSet(ViewSet):
    serializer_class = CurrencyExchangeRateSerializer
    queryset = CurrencyExchangeRate.objects.all()

    @method_decorator(cache_page(CACHE_TIME))
    def list(self, request, *args, **kwargs):
        source_currency = request.query_params.get('source_currency')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        if source_currency and date_from and date_to:
            rates = CurrencyExchangeRate.objects.filter(
                source_currency__code=source_currency,
                valuation_date__gte=date_from,
                valuation_date__lte=date_to
            )
        else:
            rates = CurrencyExchangeRate.objects.all()

        serializer = self.get_serializer(rates, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    @method_decorator(cache_page(CACHE_TIME))
    def _currency_rate_list(self, request, *args, **kwargs):
        source_currency = request.query_params.get('source_currency')
        exchanged_currency = request.query_params.get('exchanged_currency')
        valuation_date = request.query_params.get('valuation_date')

        if source_currency and exchanged_currency and valuation_date:
            rate = get_exchange_rate_data(source_currency, exchanged_currency, valuation_date)
            if rate:
                serializer = self.get_serializer(rate)
                return Response(serializer.data)
            else:
                return Response({"error": "Exchange rate not found"}, status=404)
        else:
            return Response({"error": "Missing parameters"}, status=400)


    @action(detail=False, methods=['GET'])
    @method_decorator(cache_page(CACHE_TIME))
    def currency_rate_list(self,request):

        try:
            source_currency = request.GET.get('source_currency')
            date_from = request.GET.get('date_from')
            date_to = request.GET.get('date_to')

            if not source_currency or not date_from or not date_to:
                return Response({"error": "Missing required parameters"}, status=400)

            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

            if date_from > date_to:
                return Response({"error": "'date_from' cannot be later than 'date_to'."}, status=400)

            
            available_currencies = Currency.objects.values_list('code', flat=True)  # Optimized query for available currency codes
            currency_rates = CurrencyExchangeRate.objects.filter(
                source_currency__code=source_currency,
                valuation_date__range=[date_from, date_to]
            ).values('valuation_date', 'exchanged_currency__code', 'rate_value')

            existing_dates = currency_rates.values_list('valuation_date', flat=True).distinct()
            all_dates_range = [date_from + timedelta(days=i) for i in range((date_to - date_from).days + 1)]
            missing_dates = [d for d in all_dates_range if d not in existing_dates]

            if missing_dates:
                missing_dates_str = [date.strftime('%Y-%m-%d') for date in missing_dates]
                provider_rates = get_exchange_rate_data_timeseries(source_currency, missing_dates_str[0], missing_dates_str[-1])

                source_currency_obj = Currency.objects.get(code=source_currency)

                new_rates = []
                for date, rates in provider_rates.items():
                    for currency_code, rate_value in rates.items():
                        if currency_code in available_currencies:
                            exchanged_currency = Currency.objects.get(code=currency_code)
                            new_rates.append(CurrencyExchangeRate(
                                exchanged_currency=exchanged_currency,
                                source_currency=source_currency_obj,
                                valuation_date=datetime.strptime(date, '%Y-%m-%d'),
                                rate_value=rate_value
                            ))
                
                if new_rates:
                    CurrencyExchangeRate.objects.bulk_create(new_rates)  


            all_currency_rates = CurrencyExchangeRate.objects.filter(
                source_currency__code=source_currency,
                valuation_date__range=[date_from, date_to]
            ).order_by('valuation_date').values('valuation_date', 'exchanged_currency__code', 'rate_value')

            result = {}
            for rate in all_currency_rates:
                date_str = rate['valuation_date'].strftime('%Y-%m-%d')
                if date_str not in result:
                    result[date_str] = {}
                result[date_str][rate['exchanged_currency__code']] = float(rate['rate_value'])

            return Response(result)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno,e)
            return Response({"message" : "something went wrong"})
    



        
    @action(detail=False, methods=['GET'])
    @method_decorator(cache_page(CACHE_TIME))
    def convert(self, request):
        try:
            source_currency = request.query_params.get('source_currency')
            exchanged_currency = request.query_params.get('exchanged_currency')
            amount = request.query_params.get('amount')
            current_date = date.today()
            if source_currency and exchanged_currency and amount:
                current_exchange_rate_obj = CurrencyExchangeRate.objects.filter(
                        source_currency__code=source_currency,
                        exchanged_currency__code=exchanged_currency,
                        valuation_date=current_date)
                
                if current_exchange_rate_obj.exists():
                    rate_value = float(current_exchange_rate_obj[0].rate_value)
                    converted_amount = rate_value * float(amount)
                    return Response({"converted_amount" : 
                                    converted_amount})
                else:
                    rate = get_exchange_rate_data(source_currency,
                            exchanged_currency, date.today())

                if rate:
                    converted_amount = rate.rate_value * float(amount)
                
                    return Response({"converted_amount": converted_amount})
                else:
                    return Response({"error": "Exchange rate not found"}, status=404)
            else:
                return Response({"error": "Missing parameters"}, status=400)      
            


        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno,e)
            return Response({"message" : "something went wrong"})
    
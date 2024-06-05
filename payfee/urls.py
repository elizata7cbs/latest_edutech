import os
import django

# Manually configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edutech_payment_engine.settings')
django.setup()
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from payfee.views import PaymentView

router = DefaultRouter()
router.register(r'fee-collection', PaymentView, basename='fee-collection')

urlpatterns = [
    path('', include(router.urls)),
    path('fee-collection/filter/', PaymentView.as_view({'get': 'filter_queryset'}),
         name='fee-collection-filter'),
    path('fee-collections/', PaymentView.as_view({'post': 'collect_fee'}),
         name='fee-collection'),
    path('calculate_total_fee/', PaymentView.as_view({'get': 'calculate_total_fee'}),
         name='calculate_total_fee'),

    path('api/v1/fee/list_transaction',
         PaymentView.as_view({'get': 'list_transaction'}),
         name='list_transactions'),
    path('calculate_profit/', PaymentView.as_view({'get': 'calculate_profit'}),
         name='calculate_total_fee'),

    # path('calculate_percentage_profitt/', PaymentView.as_view({'get': 'calculate_percentage_profit'}),
    #      name='calculate_percentage_profit'),

]

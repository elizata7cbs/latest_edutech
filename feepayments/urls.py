from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import FeePaymentsView
router = DefaultRouter()
router.register(r'', FeePaymentsView, basename='')


urlpatterns = [
    path('', include(router.urls)),#path('fee-payments/process_payment/', FeePaymentsView.as_view({'post': 'process_payment'}), name='fee-payments-process-payment'),
    path('fee-payments/update_balance/', FeePaymentsView.as_view({'put': 'update_balance'}), name='fee-payments-update-balance'),
    path('fee-payments/search_fee_payment/', FeePaymentsView.as_view({'get': 'search_payment'}), name='fee-payment-search-payment'),
    path('fee-payments/retrieve_fee_payment/', FeePaymentsView.as_view({'get': 'retrieve_payment'}), name='fee-payment-retrieve-payment'),
    path('fee-payments/generate_receipt/', FeePaymentsView.as_view({'get': 'generate_receipt'}), name='fee-payment-generate-receipt'),
    path('fee-payments/generate_statement/', FeePaymentsView.as_view({'get': 'generate_receipt'}), name='fee-payment-generate-statement'),
]

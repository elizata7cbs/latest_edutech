import os
import django

# Manually configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edutech_payment_engine.settings')
django.setup()
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from feecollections.views import FeeCollectionsView
from .views import FeeCollectionsView, StatementView, ReceiptView, FilterFeeCollections


router = DefaultRouter()
router.register(r'fee-collection', FeeCollectionsView, basename='fee-collection')

urlpatterns = [
    path('fee-collections/', FeeCollectionsView.as_view({'get': 'list', 'post': 'create'}), name='fee_collections_list_create'),
    path('fee-collections/<int:pk>/', FeeCollectionsView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='fee_collections_retrieve_update_destroy'),
    path('statement/', StatementView.as_view(), name='statement'),
    path('receipt/<str:receipt_number>/', ReceiptView.as_view(), name='receipt'),
    path('filter-fee-collections/', FilterFeeCollections.as_view(), name='filter_fee_collections'),
]

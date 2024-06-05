
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PaymentGroupsView
router = DefaultRouter()
router.register(r'', PaymentGroupsView, basename='')


urlpatterns = [
    path('', include(router.urls)),
   # path('payment-groups/', PaymentGroupsView.as_view({'get': 'list'}), name='payment-groups-list'),
    path('payment-groups/filter/', PaymentGroupsView.as_view({'get': 'filter_groups'}), name='payment-groups-filter'),]



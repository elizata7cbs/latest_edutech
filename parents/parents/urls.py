from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ParentsView
router = DefaultRouter()
router.register(r'', ParentsView, basename='')


urlpatterns = [
    path('parents/<int:pk>/make-payment/', ParentsView.as_view({'post': 'make_payment'}), name='make_payment'),
    path('parents/<int:pk>/fee-balance/', ParentsView.as_view({'get': 'get_fee_balance'}), name='fee_balance'),
    path('parents/<int:pk>/statement/', ParentsView.as_view({'get': 'get_statement'}), name='statement'),

]

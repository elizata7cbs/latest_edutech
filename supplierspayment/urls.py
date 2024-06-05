from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SuppliersPaymentView

router = DefaultRouter()
router.register(r'', SuppliersPaymentView, basename='')

urlpatterns = [
    path('', include(router.urls)),

    path('pay_supplier/', SuppliersPaymentView.as_view({'post': 'pay_supplier'}),
         name='pay_supplier'),
    path('list_suppliers_account/', SuppliersPaymentView.as_view({'get': 'list_suppliers_account'}),
         name='list_suppliers_account'),

]


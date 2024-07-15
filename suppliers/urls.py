from django.urls import path, include
from rest_framework.routers import DefaultRouter

from suppliers.views import SuppliersView

router = DefaultRouter()
router.register(r'', SuppliersView, basename='')

urlpatterns = [
    path('', include(router.urls)),
    path('suppliers/list_suppliers_account/', SuppliersView.as_view({'get': 'list_suppliers_account'}),
         name='list_suppliers_account'),

    path('suppliers/calculate_total_amount/', SuppliersView.as_view({'get': 'calculate_total_amount'}),
         name='calculate_total_amount'),

    path('suppliers/listsupplier', SuppliersView.as_view({'get': 'listsupplier'}),
         name='listsupplier'),

]

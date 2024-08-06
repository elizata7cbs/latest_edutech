from django.urls import path, include
from rest_framework.routers import DefaultRouter

from fee.views import StudentFeeCategoriesView

router = DefaultRouter()
router.register(r'fee', StudentFeeCategoriesView, basename='fee')

urlpatterns = [
    path('', include(router.urls)),
    path('api/v1/fee/fee structure/get_fee_structure/<int:student_id>/',
         StudentFeeCategoriesView.as_view({'get': 'get_fee_structure'}),
         name='get_fee_structure'),
    path('api/v1/fee/list_category_records',
         StudentFeeCategoriesView.as_view({'get': 'list_category_records'}),
         name='list_category_records'),
    path('api/v1/fee/percentage_of_each_category',
         StudentFeeCategoriesView.as_view({'get': 'percentage_of_each_category'}),
         name='percentage_of_each_category'),

]

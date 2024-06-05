from django.urls import path, include
from rest_framework.routers import DefaultRouter

from feecategories.views import FeeCategoriesView

router = DefaultRouter()
router.register(r'fee-categories', FeeCategoriesView, basename='fee-categories')

urlpatterns = [
    path('', include(router.urls)),
    path('fee/filter/', FeeCategoriesView.as_view({'get': 'filter_categories'}),
         name='fee-categories-filter'),
    path('categories/create/', FeeCategoriesView.as_view({'post': 'createfeecategories'}),
         name='create-feecategories'),
    #path('categories/calculate_total_amount/', FeeCategoriesView.as_view({'get': 'calculate_total_amount'}),
        # name='calculate_total_amount'),
    path('categories/list_virtual_account', FeeCategoriesView.as_view({'get': 'list_virtual_account'}),
         name='list_virtual_account'),
    # path('calculate_student_total_fee', FeeCategoriesView.as_view({'get': 'calculate_student_total_fee'}),
    #      name='calculate_student_total_fee'),
    # path('categories/calculate_student_total_fee/<int:student_id>/',
    #      FeeCategoriesView.as_view({'get': 'calculate_student_total_fee'}),
    #      name='calculate_total_fee'),


]

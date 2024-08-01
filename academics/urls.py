
from rest_framework import routers
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from academics.views import AcademicYearView

router = DefaultRouter()
router.register(r'', AcademicYearView, basename='')

urlpatterns = [
    # path('filter-users/<str:str>', AcademicYearView.as_view({'get': 'filter_users'}), name='filter_users'),
    path('create/', AcademicYearView.as_view({'post': 'create'}), name='create'),
    path('update/<int:pk>', AcademicYearView.as_view({'put': 'update'}), name='update'),
    path('delete/<int:pk>', AcademicYearView.as_view({'delete': 'destroy'}), name='destroy'),
    path('list/', AcademicYearView.as_view({'get': 'list'}), name='list'),
    path('retrieve/<int:pk>', AcademicYearView.as_view({'get': 'retrieve'}), name='retrieve'),

    path('update_profile/', AcademicYearView.as_view({'put': 'update_profile'}), name='update_profile'),
]

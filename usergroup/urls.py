from rest_framework import routers
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserGroupView
router = DefaultRouter()
router.register(r'', UserGroupView, basename='')

urlpatterns = [
    path('list/', UserGroupView.as_view({'get': 'list'}), name='list'),
    path('create/', UserGroupView.as_view({'post': 'create'}), name='create'),

]


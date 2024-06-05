from rest_framework import routers
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserGroupView
router = DefaultRouter()
router.register(r'', UserGroupView, basename='')

urlpatterns = [
    # path('', include(router.urls)),
    path('create/', UserGroupView.as_view({'post': 'create'}), name='create'),
path('list/', UserGroupView.as_view({'get': 'list'}), name='list'),
path('update/', UserGroupView.as_view({'put': 'update'}), name='update'),
path('delete/', UserGroupView.as_view({'delete': 'delete'}), name='delete'),
]


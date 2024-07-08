
from rest_framework import routers
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomUserView, PermissionsView

router = DefaultRouter()
router.register(r'', CustomUserView, basename='')

urlpatterns = [
    # path('', include(router.urls)),
    path('filter-users/<str:str>', CustomUserView.as_view({'get': 'filter_users'}), name='filter_users'),
    path('create/permission/', PermissionsView.as_view({'post': 'create'}), name='create'),
    path('list/permissions/', PermissionsView.as_view({'get': 'list'}), name='list'),
    path('revoke/token/', PermissionsView.as_view({'post': 'revoke_token'}), name='revoke_token'),
    path('give/permissions/', PermissionsView.as_view({'post': 'give_permissions'}), name='give_permissions'),
    path('update/<int:pk>', CustomUserView.as_view({'put': 'update'}), name='update'),
    path('delete/<int:pk>', CustomUserView.as_view({'delete': 'destroy'}), name='destroy'),
    path('list/', CustomUserView.as_view({'get': 'list'}), name='list'),
    path('create/', CustomUserView.as_view({'post': 'create'}), name='create'),
    path('retrieve/<int:pk>', CustomUserView.as_view({'get': 'retrieve'}), name='retrieve'),
    path('deactivate/<str:email>', CustomUserView.as_view({'post': 'deactivate'}), name='deactivate'),
    path('update_profile/', CustomUserView.as_view({'put': 'update_profile'}), name='update_profile'),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import FeeExtensionsView
router = DefaultRouter()
router.register(r'', FeeExtensionsView, basename='')


urlpatterns = [
    path('', include(router.urls)),
]


from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PaymentModesView
router = DefaultRouter()
router.register(r'', PaymentModesView, basename='')


urlpatterns = [
    path('', include(router.urls)),
   ]


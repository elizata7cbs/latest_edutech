from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import InquiriesView
router = DefaultRouter()
router.register(r'', InquiriesView , basename='')


urlpatterns = [
    path('', include(router.urls)),



]

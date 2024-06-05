from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SchoolsViewSet

router = DefaultRouter()
router.register(r'schools', SchoolsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
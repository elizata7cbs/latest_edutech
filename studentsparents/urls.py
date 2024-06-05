from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import StudentsParentsView
router = DefaultRouter()
router.register(r'', StudentsParentsView, basename='')


urlpatterns = [
    path('', include(router.urls)),
]

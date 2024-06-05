from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import StudentsSchoolsView
router = DefaultRouter()
router.register(r'', StudentsSchoolsView, basename='')


urlpatterns = [
    path('', include(router.urls)),
]

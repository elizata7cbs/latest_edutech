from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ExpenseTypesView

expensetypes = DefaultRouter()
expensetypes.register(r'', ExpenseTypesView, basename='')


urlpatterns = [
    path('', include(expensetypes.urls)),
]


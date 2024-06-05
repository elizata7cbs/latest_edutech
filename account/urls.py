from django.urls import path
from . import views
from .views import AccountListAPIView

urlpatterns = [
    path('account/', AccountListAPIView.as_view(), name='account-list'),
    path('accounts/<int:pk>/balance/', views.AccountBalanceAPIView.as_view(), name='account-balance'),
    path('accounts/<int:pk>/debit/', views.AccountDebitAPIView.as_view(), name='account-debit'),
]


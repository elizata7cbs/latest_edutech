from django.urls import path
from .views import ExpensePaymentAPIView

urlpatterns = [
    path('api/expense-payment/', ExpensePaymentAPIView.as_view(), name='expense-payment'),
]

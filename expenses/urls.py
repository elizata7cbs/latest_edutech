from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExpenseListAPIView, ExpensePaymentAPIView, ExpenseDetailAPIView, ExpenseStatsView, ExpenseUpdateAPIView

router = DefaultRouter()

urlpatterns = [
    path('expenses/', ExpenseListAPIView.as_view(), name='expense-list'),
    path('expenses/<int:pk>/', ExpenseDetailAPIView.as_view(), name='expense-detail'),
    path('expenses/<int:expense_id>/update/', ExpenseUpdateAPIView.as_view(), name='expense-update'),
    path('expenses/stats/', ExpenseStatsView.as_view(), name='expense-stats'),
    path('expenses/payment/', ExpensePaymentAPIView.as_view(), name='expense-payment'),
    path('', include(router.urls)),
]

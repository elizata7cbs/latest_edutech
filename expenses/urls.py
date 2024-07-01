from django.urls import path
from .views import ExpenseListAPIView, ExpenseDetailAPIView, ExpenseStatsView

urlpatterns = [
    path('expenses/', ExpenseListAPIView.as_view(), name='expense-list'),
    path('expenses/<int:pk>/', ExpenseDetailAPIView.as_view(), name='expense-detail'),
    path('expense-stats/', ExpenseStatsView.as_view(), name='expense-stats'),
]

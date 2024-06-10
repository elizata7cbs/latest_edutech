from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExpenseListAPIView,  ExpenseDetailAPIView, ExpenseStatsView, \
    ExpenseUpdateAPIView, ExpenseTypeUpdateAPIView,ExpensePaymentAPIView

router = DefaultRouter()

urlpatterns = [
    path('expenses/', ExpenseListAPIView.as_view(), name='expense-list'),
    path('expenses/<int:pk>/', ExpenseDetailAPIView.as_view(), name='expense-detail'),
    path('expenses/<int:pk>/update/', ExpenseUpdateAPIView.as_view(), name='expense-update'),  # Use 'pk' instead of 'expense_id'
    path('expenses/stats/', ExpenseStatsView.as_view(), name='expense-stats'),
    path('expense/payment/', ExpensePaymentAPIView.as_view(), name='expense-payment'),
    path('expense-types/<int:pk>/update/', ExpenseTypeUpdateAPIView.as_view(), name='expense-type-update'),
    path('', include(router.urls)),
]

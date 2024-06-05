import logging
from datetime import datetime
import django_filters
from django.db.models import Sum
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from account.models import Account
from .models import Expenses
from .serializers import ExpensesSerializer, ExpensePaymentSerializer
from rest_framework import status

logger = logging.getLogger(__name__)


class ExpensesFilter(django_filters.FilterSet):
    term = django_filters.CharFilter(field_name='term', lookup_expr='icontains')
    month = django_filters.CharFilter(method='filter_by_month')

    class Meta:
        model = Expenses
        fields = ['term', 'month']

    def filter_by_month(self, queryset, name, value):
        try:
            month_number = datetime.strptime(value, '%B').month
            return queryset.filter(datePosted__month=month_number)
        except ValueError:
            return queryset.none()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ExpenseListAPIView(APIView):
    @swagger_auto_schema(
        operation_description="List all expenses and display total expenses",
        responses={200: ExpensesSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('term', openapi.IN_QUERY, description="Filter by term or semester",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('month', openapi.IN_QUERY, description="Filter by month (e.g., 'January')",
                              type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request):
        term = request.GET.get('term')
        month = request.GET.get('month')
        filters = {}
        if term:
            filters['term'] = term
        if month:
            try:
                filters['datePosted__month'] = datetime.strptime(month, '%B').month
            except ValueError as e:
                logger.error(f"Invalid month value provided: {month}")
                return Response({"detail": "Invalid month value provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            expenses = Expenses.objects.filter(**filters)
            total_expenses = sum(expense.amount for expense in expenses)
            serializer = ExpensesSerializer(expenses, many=True)
            return Response({
                "total_expenses": total_expenses,
                "expenses": serializer.data
            })
        except ValueError as e:
            logger.error(f"Error filtering expenses: {e}")
            return Response({"detail": "An error occurred while processing the request."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Create a new expense",
        request_body=ExpensesSerializer,
        responses={201: ExpensesSerializer()}
    )
    def post(self, request):
        expense_serializer = ExpensesSerializer(data=request.data)
        if expense_serializer.is_valid():
            expense = expense_serializer.save()
            if request.FILES.get('receipt'):
                expense.receipt = request.FILES['receipt']
                expense.save()
            return Response(expense_serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Validation errors: {expense_serializer.errors}")
        return Response(expense_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpenseDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Expenses.objects.get(pk=pk)
        except Expenses.DoesNotExist:
            raise Http404

    @swagger_auto_schema(
        operation_description="Retrieve an expense by ID",
        responses={200: ExpensesSerializer()}
    )
    def get(self, request, pk):
        expense = self.get_object(pk)
        serializer = ExpensesSerializer(expense)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update an existing expense",
        request_body=ExpensesSerializer,
        responses={200: ExpensesSerializer()}
    )
    def put(self, request, pk):
        expense = self.get_object(pk)
        serializer = ExpensesSerializer(expense, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete an expense by ID",
        responses={204: "No Content"}
    )
    def delete(self, request, pk):
        expense = self.get_object(pk)
        expense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExpenseUpdateAPIView(APIView):
    def patch(self, request, expense_id):
        try:
            expense = Expenses.objects.get(pk=expense_id)
        except Expenses.DoesNotExist:
            return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ExpensesSerializer(expense, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpenseStatsView(View):
    @swagger_auto_schema(
        operation_description="Retrieve expense statistics",
        manual_parameters=[
            openapi.Parameter('term', openapi.IN_QUERY, description="Filter by term or semester",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('month', openapi.IN_QUERY, description="Filter by month (e.g., 'January')",
                              type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request):
        term = request.GET.get('term')
        month = request.GET.get('month')
        filters = {}
        if term:
            filters['term'] = term
        if month:
            try:
                filters['datePosted__month'] = datetime.strptime(month, '%B').month
            except ValueError as e:
                logger.error(f"Invalid month value provided: {month}")
                return JsonResponse({'detail': 'Invalid month value provided.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            total_expenses = Expenses.objects.filter(**filters).aggregate(total=Sum('amount'))['total'] or 0
            return JsonResponse({'total_expenses': total_expenses})
        except ValueError as e:
            logger.error(f"Error calculating total expenses: {e}")
            return JsonResponse({'detail': 'An error occurred while processing the request.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExpensePaymentAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Pay for an expense",
        request_body=ExpensePaymentSerializer,
        responses={201: "Expense paid successfully"}
    )
    def post(self, request):
        serializer = ExpensePaymentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Save the payment
                serializer.save()
                return Response({"detail": "Expense paid successfully"}, status=status.HTTP_201_CREATED)
            except ValueError as ve:
                return Response({"detail": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

import logging
from datetime import datetime

from django.db.models import Sum
from django.http import Http404, JsonResponse
from django.views import View
from rest_framework import status, permissions, authentication
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Expenses
from .serializers import ExpensesSerializer

logger = logging.getLogger(__name__)


class ExpenseListAPIView(APIView):
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            expenses = self.get_queryset()
            logger.debug(f"Retrieved {expenses.count()} expenses.")

            total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
            logger.debug(f"Total expenses calculated: {total_expenses}")

            serializer = self.get_serializer(expenses, many=True)
            logger.debug(f"Serialized {len(serializer.data)} expenses.")

            return Response({
                "total_expenses": total_expenses,
                "expenses": serializer.data
            })
        except Expenses.DoesNotExist:
            logger.error("Expenses do not exist.")
            raise Http404("Expenses not found.")
        except Exception as e:
            logger.error(f"Error retrieving expenses: {e}")
            return Response({"detail": "An error occurred while processing the request."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        return Expenses.objects.all()

    def get_serializer(self, *args, **kwargs):
        return ExpensesSerializer(*args, **kwargs)

    def post(self, request):
        expense_serializer = self.get_serializer(data=request.data)
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
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Expenses.objects.get(pk=pk)
        except Expenses.DoesNotExist:
            logger.error(f"Expense with ID {pk} does not exist.")
            raise Http404("Expense not found.")

    def get(self, request, pk):
        expense = self.get_object(pk)
        serializer = ExpensesSerializer(expense)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            expense = self.get_object(pk)
            serializer = ExpensesSerializer(expense, data=request.data, partial=True)  # Allow partial updates
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                logger.error(f"Validation errors during expense update: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating expense with ID {pk}: {e}")
            return Response({"detail": "An error occurred while processing the request."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        try:
            expense = self.get_object(pk)
            expense.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error deleting expense with ID {pk}: {e}")
            return Response({"detail": "An error occurred while processing the request."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExpenseStatsView(View):
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        term = request.GET.get('term')
        month = request.GET.get('month')
        filters = {}

        if term:
            filters['term__icontains'] = term
        if month:
            try:
                filters['datePosted__month'] = datetime.strptime(month, '%B').month
            except ValueError:
                logger.error(f"Invalid month value provided: {month}")
                return JsonResponse({'detail': 'Invalid month value provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            total_expenses = Expenses.objects.filter(**filters).aggregate(total=Sum('amount'))['total'] or 0
            logger.debug(f"Total expenses for filters {filters}: {total_expenses}")
            return JsonResponse({'total_expenses': total_expenses})
        except Exception as e:
            logger.error(f"Error calculating total expenses with filters {filters}: {e}")
            return JsonResponse({'detail': 'An error occurred while processing the request.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .serializers import ExpenseTypesSerializer
from .models import ExpenseTypes


class ExpenseTypesView(ModelViewSet):
    queryset = ExpenseTypes.objects.all()
    serializer_class = ExpenseTypesSerializer
    # permission_classes = [IsAuthenticated]  # Require authentication

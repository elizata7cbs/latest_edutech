from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
import logging

from .serializers import ExpenseTypesSerializer
from .models import ExpenseTypes

logger = logging.getLogger(__name__)

class ExpenseTypesView(ModelViewSet):
    queryset = ExpenseTypes.objects.all()
    serializer_class = ExpenseTypesSerializer
    permission_classes = [IsAuthenticated]  # Require authentication

    def list(self, request, *args, **kwargs):
        logger.debug("Listing all expense types")
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        logger.debug(f"Creating a new expense type with data: {request.data}")
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        logger.debug(f"Retrieving expense type with id: {kwargs.get('pk')}")
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        logger.debug(f"Updating expense type with id: {kwargs.get('pk')} with data: {request.data}")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        logger.debug(f"Deleting expense type with id: {kwargs.get('pk')}")
        return super().destroy(request, *args, **kwargs)

from django.db import models
from feecategories.models import FeeCategories  # Assuming this is the model for fee_categories

class PaymentGroups(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=500)
    status = models.IntegerField(default=1)
    dateCreated = models.DateField(auto_now_add=True)

class Meta:
        db_table = 'payment_groups'

def str(self):
        return f"Payment Groups ID: {self.id}, Fee Categories: {self.feeID}"
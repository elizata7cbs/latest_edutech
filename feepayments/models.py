from django.db import models

# Create your models here.
from students.models import Students
from feecategories.models import FeeCategories


class FeePayments(models.Model):
    id=models.AutoField(primary_key=True)
    studentID = models.ForeignKey(Students, on_delete=models.CASCADE)
    feecategory = models.ForeignKey(FeeCategories, on_delete=models.CASCADE)
    uniqueid=models.CharField(max_length=10)
    referenceNO = models.CharField(max_length=100)
    amountPaid = models.DecimalField(max_digits=10, decimal_places=2)  # Adjusted to use DecimalField for currency autogeneration
    datePosted = models.DateField(auto_now_add=True)
    # sessionID = models.ForeignKey(SystemInfo, on_delete=models.CASCADE)

    class Meta:
        db_table = 'fee_payments'
        verbose_name_plural = 'Fee Payments'

    def _str_(self):
        return self.uniqueid, self.id
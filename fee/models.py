from decimal import Decimal

from django.db import models

from feecategories.models import FeeCategories, VirtualAccount
from students.models import Students


class StudentFeeCategories(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    fee_category = models.ForeignKey(FeeCategories, on_delete=models.CASCADE)

    # amount = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"{self.student} "

    class Meta:
        db_table = 'StudentFeeCategories'  # Optional: specify the database table name


class FeeCategoryTransaction(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    feecategory = models.ForeignKey(FeeCategories, on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=255)
    debit = models.DecimalField(max_digits=10, decimal_places=2)
    credit = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    transaction_date = models.DateField(auto_now_add=True)
    firstName =models.CharField(max_length=255, blank=True)
    middleName = models.CharField(max_length=255, blank=True)


    def save(self, *args, **kwargs):
        # Calculate the balance if not set
        if self.balance is None:
            # Get the previous transaction for the same student and fee category
            previous_transaction = FeeCategoryTransaction.objects.filter(
                student=self.student,
                feecategory=self.feecategory
            ).order_by('-transaction_date').first()

            if previous_transaction:
                previous_balance = previous_transaction.balance
            else:
                previous_balance = Decimal('0.00')

            self.balance = previous_balance + self.credit - self.debit

        super(FeeCategoryTransaction, self).save(*args, **kwargs)

    class Meta:
        db_table = 'fee_category_transactions'

    def __str__(self):
        return f'{self.student.name} - {self.feecategory.name if self.feecategory else "No Category"} - {self.description}'

from django.db import models
from decimal import Decimal
from django.utils.crypto import get_random_string

from expensetypes.models import ExpenseTypes


class Expenses(models.Model):
    id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Expense Amount")
    expensetypes = models.ForeignKey(ExpenseTypes, on_delete=models.CASCADE, verbose_name="Expense Type", related_name='expenses')
    expenseID = models.CharField(max_length=10, unique=True, verbose_name="Unique Expense ID", default="TEMP")
    currency = models.CharField(max_length=10, verbose_name="Currency", default="KES")  # Default to KES

    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
    )

    datePosted = models.DateField(auto_now_add=True, verbose_name="Date Posted")
    approved = models.BooleanField(default=False, verbose_name="Approved")
    receipt = models.FileField(upload_to='receipts/', blank=True)  # Ensure this field is defined only once
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    is_deleted = models.BooleanField(default=False)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    remaining_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'), verbose_name="Remaining Balance")

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def delete(self, *args, **kwargs):
        self.soft_delete()

    def approve(self):
        self.status = self.APPROVED
        self.save()

    def reject(self):
        self.status = self.REJECTED
        self.save()

    def save(self, *args, **kwargs):
        # Ensure amount_paid is not None
        if self.amount_paid is None:
            self.amount_paid = Decimal('0.00')

        # Calculate remaining balance
        self.remaining_balance = self.amount - self.amount_paid

        # Generate a unique expenseID if it is still "TEMP"
        if self.expenseID == "TEMP":
            self.expenseID = self.generate_unique_expense_id()

        super().save(*args, **kwargs)

    def generate_unique_expense_id(self):
        unique_id = get_random_string(length=10)
        while Expenses.objects.filter(expenseID=unique_id).exists():
            unique_id = get_random_string(length=10)
        return unique_id

    def __str__(self):
        return self.expenseID

    class Meta:
        db_table = 'expenses'

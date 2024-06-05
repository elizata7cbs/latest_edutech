from django.db import models
from django.utils.crypto import get_random_string
from decimal import Decimal  # Import Decimal

from account.models import Account
from expensetypes.models import ExpenseTypes

class Expenses(models.Model):
    id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Expense Amount")
    expensetypes = models.ForeignKey(ExpenseTypes, on_delete=models.CASCADE, verbose_name="Expense Type",
                                     related_name='expenses')
    expenseID = models.CharField(max_length=10, unique=True, verbose_name="Unique Expense ID", default="TEMP")

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
    receipt = models.FileField(upload_to='receipts/', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    is_deleted = models.BooleanField(default=False)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))  # Set default value
    remaining_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'),
                                            verbose_name="Remaining Balance")

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
        if self.expenseID == "TEMP" or not self.expenseID:
            last_expense = Expenses.objects.order_by('-id').first()
            if not last_expense or last_expense.expenseID == "TEMP":
                new_expenseID = "Ex001"
            else:
                last_expense_number = int(last_expense.expenseID.split('Ex')[1])
                new_expenseID = f"Ex{last_expense_number + 1:03d}"
            self.expenseID = new_expenseID

        # Ensure amount_paid is not None
        if self.amount_paid is None:
            self.amount_paid = Decimal('0.00')

        # Calculate remaining balance
        self.remaining_balance = self.amount - self.amount_paid

        super().save(*args, **kwargs)

    def __str__(self):
        return self.expenseID

    class Meta:
        db_table = 'expenses'

class ExpensePayment(models.Model):
    id = models.AutoField(primary_key=True)
    expense = models.ForeignKey(Expenses, on_delete=models.CASCADE, related_name='payments')
    debited_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True)
    payment_details = models.TextField(null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2)
    date_paid = models.DateField(auto_now_add=True)
    reference_number = models.CharField(max_length=10, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = get_random_string(length=10)
        if not self.debited_account:
            raise ValueError("No account linked to this expense")
        if self.debited_account.balance < self.amount_paid:
            raise ValueError("Insufficient funds in the account")

        self.debited_account.balance -= self.amount_paid
        self.debited_account.save()

        # Ensure amount_paid is not None
        if self.expense.amount_paid is None:
            self.expense.amount_paid = Decimal('0.00')

        self.expense.amount_paid += self.amount_paid
        self.expense.save()  # Let the Expense model handle remaining_balance update

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment for {self.expense.expenseID}"

    class Meta:
        db_table = 'expense_payments'

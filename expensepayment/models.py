from django.db import models, transaction
from django.utils.crypto import get_random_string
from decimal import Decimal
from account.models import Account
from expenses.models import Expenses


class ExpensePayment(models.Model):
    id = models.AutoField(primary_key=True)
    expense = models.ForeignKey(Expenses, on_delete=models.CASCADE, related_name='payments')
    debited_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True)
    payment_details = models.TextField(null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2)
    date_paid = models.DateField(auto_now_add=True)
    reference_number = models.CharField(max_length=10, unique=True, editable=False)
    source_account = models.CharField(max_length=20, blank=True)
    destination_account = models.CharField(max_length=20, blank=True)

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = get_random_string(length=10)

        if not self.debited_account:
            raise ValueError("No account linked to this expense")

        if self.debited_account.balance < self.amount_paid:
            raise ValueError("Insufficient funds in the account")

        with transaction.atomic():
            self.debited_account.balance -= self.amount_paid
            self.debited_account.save(update_fields=['balance'])

            self.expense.amount_paid += self.amount_paid
            self.expense.remaining_balance -= self.amount_paid
            self.expense.save(update_fields=['amount_paid', 'remaining_balance'])

            super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment for {self.expense.expenseID}"

    class Meta:
        db_table = 'expense_payments'


class InsufficientFundsError(Exception):
    pass


class NoLinkedAccountError(Exception):
    pass

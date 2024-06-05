from django.db import models


class Account(models.Model):
    account_name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return self.account_name

    def debit(self, amount):
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self.save()
        return self.balance

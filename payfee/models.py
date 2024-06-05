from django.db import models

from students.models import Students


class Payments(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE, to_field='uniqueId')  # Use uniqueId
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    paymentmode = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=250)
    payment_date = models.DateField(auto_now_add=True)
    reference = models.CharField(max_length=255)


    class Meta:
        db_table = 'Payments'


class RecordTransaction(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    debit = models.DecimalField(max_digits=10, decimal_places=2)
    credit = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    transaction_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'recordtransaction'

    def save(self, *args, **kwargs):
        self.balance = self.debit - self.credit
        super(RecordTransaction, self).save(*args, **kwargs)


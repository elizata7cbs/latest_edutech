from django.db import models
from django.utils.crypto import get_random_string
from feecategories.models import FeeCategories
from schools.models import Schools
from students.models import Students
from django.db.models import Max

# from utils.Helpers import Helpers


class FeeCollections(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('mobile_wallet', 'Mobile Wallet'),
        ('Equity_bank_mobile_app', 'Equity Bank Mobile App'),
        ('Bank_cards', 'Bank Cards'),
        ('Bank_agent', 'Bank Agent'),
        ('Bank_over_the_counter', 'Banking Over the Counter'),
    ]

    id = models.AutoField(primary_key=True)
    studentId = models.ForeignKey(Students, on_delete=models.CASCADE)
    feecategory = models.ForeignKey(FeeCategories, on_delete=models.CASCADE)
    uniqueid = models.CharField(max_length=10)
    school = models.ForeignKey(Schools, on_delete=models.CASCADE)
    payment_reference = models.CharField(max_length=50)
    amountPaid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    school_code = models.CharField(max_length=50)
    debit = models.DecimalField(max_digits=10, decimal_places=2)
    credit = models.DecimalField(max_digits=10, decimal_places=2)
    outstandingbalance = models.DecimalField(max_digits=10, decimal_places=2)
    grade = models.CharField(max_length=20)
    receipt_number = models.CharField(max_length=100, unique=True, blank=True)
    payment_mode = models.CharField(max_length=50, choices=PAYMENT_MODE_CHOICES)

    class Meta:
        db_table = 'fee_collections'
        verbose_name_plural = 'Fee Collections'

    def save(self, *args, **kwargs):
        # helper = Helpers()
        if not self.receipt_number:
            # Generate receipt number if not provided
            self.receipt_number = Helpers.generate_receipt_number()

        # Compute outstanding balance
        self.outstandingbalance = self.compute_outstanding_balance()
        super().save(*args, **kwargs)

    def compute_outstanding_balance(self):
        return self.debit - self.credit


class Transaction(models.Model):
    studentId = models.ForeignKey(Students, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    debit = models.DecimalField(max_digits=10, decimal_places=2)
    credit = models.DecimalField(max_digits=10, decimal_places=2)
    outstandingbalance = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'transactions'

    def save(self, *args, **kwargs):
        # Compute outstanding balance based on debit and credit
        self.outstandingbalance = self.debit - self.credit
        super().save(*args, **kwargs)

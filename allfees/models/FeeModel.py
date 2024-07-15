
from django.db import models
from students.models import Students
from feecategories.models import FeeCategories
from schools.models import Schools
class FeeCollectionsAll(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('mobile_wallet', 'Mobile Wallet'),
        ('Equity_bank_mobile_app', 'Equity Bank Mobile App'),
        ('Bank_cards', 'Bank Cards'),
        ('M-Pesa', 'M-Pesa'),
        ('Cash', 'Cash'),
        ('Bank_agent', 'Bank Agent'),
        ('Bank_over_the_counter', 'Banking Over the Counter'),
    ]

    id = models.AutoField(primary_key=True)
    studentId = models.ForeignKey(Students, on_delete=models.CASCADE)
    feecategory = models.ForeignKey(FeeCategories, on_delete=models.CASCADE)
    school = models.ForeignKey(Schools, on_delete=models.CASCADE)
    payment_reference = models.CharField(max_length=50)
    amountPaid = models.FloatField()
    payment_date = models.DateField(auto_now_add=True)
    school_code = models.CharField(max_length=50)
    debit = models.FloatField
    credit = models.FloatField()
    type = models.CharField(max_length=5, null=True, blank=True)
    outstandingbalance = models.FloatField()
    grade = models.CharField(max_length=20)
    receipt_number = models.CharField(max_length=100, unique=True, blank=True)
    payment_mode = models.CharField(max_length=50, choices=PAYMENT_MODE_CHOICES)
    tran_date = models.DateField(auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'fee_collections_all'

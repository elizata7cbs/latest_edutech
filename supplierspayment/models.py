from django.db import models

from suppliers.models import Suppliers


# Create your models here.
class SuppliersPayment(models.Model):
    id = models.AutoField(primary_key=True)
    reference = models.CharField(max_length=100)
    paymentmode = models.CharField(max_length=255)
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'supplierspayment'


from django.db import models

# Create your models here.
class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    amount = models.FloatField()
    ref_number = models.CharField(max_length=50)
    type = models.CharField(max_length=10)
    tran_date= models.DateField(auto_now_add=True)
    status = models.IntegerField()
    tran_category=models.CharField(max_length=200)
    class Meta:
        db_table = 'all_transactions'

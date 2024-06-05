import datetime

from django.db import models

# Create your models here.
from django.db import models


class Suppliers(models.Model):
    id = models.AutoField(primary_key=True)
    businessName = models.CharField(max_length=255)
    supplieridNO = models.CharField(max_length=255)
    prefix = models.CharField(max_length=255)
    firstname = models.CharField(max_length=255)
    middlename = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    phoneNumber = models.CharField(max_length=255)
    altPhone = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    postalCode = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    openingBalance = models.FloatField()
    dateCreated = models.DateField(auto_now_add=True)
    status = models.IntegerField(default=1)


    class Meta:
        db_table = 'suppliers'

    def str(self):
        return self.businessName


class SuppliersAccount(models.Model):
    supplier = models.OneToOneField(Suppliers, on_delete=models.CASCADE)
    debit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField(auto_now_add=True)

    @property
    def balance(self):
        # Calculate the balance
        return self.debit - self.credit

    def __str__(self):
        # Return a string representation of the object
        return f"Supplier: {self.supplier}, Balance: {self.balance}"



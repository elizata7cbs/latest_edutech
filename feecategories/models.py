from django.db import models


class FeeCategories(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    categorycode = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    grade = models.CharField(max_length=100, choices=(
        ('PRIMARY', 'Primary'),
        ('SECONDARY', 'Secondary'),
        ('TERTIARY', 'Tertiary'),
        ('OTHER', 'Other'),
    ))
    term = models.CharField(max_length=12, choices=(
        ('Term1', 'Term1'),
        ('Term2', 'Term2'),
        ('Term3', 'Term3'),
    ))
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    apply = models.CharField(max_length=8, choices=(
        ('ALL', 'All'),
        ('OPTIONAL', 'OPTIONAL'),
    ))
    datePosted = models.DateField(auto_now_add=True)
    status = models.IntegerField(default=0)

    class Meta:
        db_table = 'fee_categories'


class VirtualAccount(models.Model):
    category = models.OneToOneField(FeeCategories, on_delete=models.CASCADE)
    debit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def str(self):
        return self.balance

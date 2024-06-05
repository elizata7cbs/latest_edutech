import datetime

from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import AbstractUser
from django.db import models

from students.models import Students
from users.models import CustomUser  # Assuming your User model is in an app named 'users'


class Parents(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    parentIdno = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=250)
    firstLogin = models.CharField(max_length=1, default="Y")
    deletedFlag = models.CharField(max_length=1, default="N")
    status = models.IntegerField(default=0)
    dateCreated = models.DateField(auto_now_add=True)


    parentType_choices = [
        ('Mother', 'Mother'),
        ('Father', 'Father'),
        ('Guardian', 'Guardian'),
        ('Sponsor', 'Sponsor'),
    ]
    parentType = models.CharField(max_length=8, choices=parentType_choices)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def _str_(self):
        return self.parentName

    class Meta:
        db_table = 'parents'  # Optional: specify the database table name

import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from users.models import CustomUser  # Assuming your User model is in an app named 'users'

from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from utils.ApiResponse import ApiResponse  # Assuming you have this utility class
from students.models import Students



class Parents(models.Model):
    id = models.AutoField(primary_key=True)
    parentName = models.CharField(max_length=250)
    parentIdno = models.CharField(max_length=250)
    parentPhone = models.CharField(max_length=250)
    username = models.CharField(max_length=100, default='default_username')
    password = models.CharField(max_length=100)
    firstLogin = models.CharField(max_length=1, default="Y")
    deletedFlag = models.CharField(max_length=1, default="N")
    status = models.IntegerField(default=0)
    dateCreated = models.DateField(auto_now_add=True)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='parents', null=True,
                                blank=True)
    accountno = models.IntegerField()
    parentType_choices = [
        ('Mother', 'Mother'),
        ('Father', 'Father'),
        ('Guardian', 'Guardian'),
        ('Sponsor', 'Sponsor'),
    ]
    parentType = models.CharField(max_length=8, choices=parentType_choices)


    def _str_(self):
        return self.parentName

    def save(self, *args, **kwargs):
        # Hash the password before saving
        self.password = make_password(self.password)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'parents'  # Optional: specify the database table name
    def get_fee_balance(self):

        pass

    def get_statement(self):

        pass
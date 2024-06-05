import datetime
from datetime import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser

from schools.models import Schools
from usergroup.models import UserGroup


class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    middle_name = models.CharField(max_length=30, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    nationality = models.CharField(max_length=30, blank=True, null=True)
    schools = models.ForeignKey(Schools, on_delete=models.CASCADE)
    usergroup = models.ForeignKey(UserGroup, on_delete=models.CASCADE, blank=True, null=True)
    is_verified = models.BooleanField

    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        help_text='',
        related_name="customuser_groups",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_permissions",
        related_query_name="customuser",
    )

    def str(self):
        return self.username

    class Meta:
        db_table = 'users'

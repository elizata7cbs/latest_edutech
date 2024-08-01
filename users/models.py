from django.db import models
from django.contrib.auth.models import AbstractUser, Group

from schools.models import Schools


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
    schools = models.ForeignKey(Schools, on_delete=models.CASCADE, null=True, blank=True)
    usergroup = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=100, default=None, null=True)
    first_login = models.BooleanField(default=True)

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

    class Meta:
        db_table = 'users'

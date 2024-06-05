
from django.db import models
from feecategories.models import FeeCategories
from schools.models import Schools
from students.models import Students
from datetime import timedelta, datetime
from django.utils import timezone
# from feecollections.models import FeeCollections
from django.contrib.auth.models import User


class FeeExtensions(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    student_unique_id = models.CharField(max_length=50)  # Unique ID of the student
    feecategory = models.ForeignKey(FeeCategories, on_delete=models.CASCADE)
    dueDate = models.DateField(null=True)
    school_code = models.ForeignKey(Schools, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    frequency_choices = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('bi_weekly', 'Bi-Weekly'),
        ('monthly', 'Monthly'),
    ]
    frequency = models.CharField(max_length=20, choices=frequency_choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    last_reminder_sent = models.DateField(null=True, blank=True)
    reminder_frequency = models.IntegerField(default=3)  # Number of days between reminders

    def __str__(self):
        return f"FeeExtension ID: {self.id}, Student: {self.student}, Fee Category: {self.feecategory}, Start Date: {self.start_date}, End Date: {self.end_date}"
    class Meta:
        db_table = 'fee_extensions'


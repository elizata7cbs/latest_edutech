import datetime
from django.db import models
from parents.models import Parents

class Inquiries(models.Model):
    id = models.AutoField(primary_key=True)
    message = models.TextField(help_text="The content of the inquiry message.")
    parentID = models.IntegerField()
    schoolID = models.IntegerField()
    status_choices = [
        ('Pending', 'Pending'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='Pending', help_text="The current status of the inquiry.")
    date = models.DateTimeField(auto_now_add=True, help_text="The date and time when the inquiry was submitted.")

    def __str__(self):
        return f"Inquiry from {self.parent.parentName} - Status: {self.status}"

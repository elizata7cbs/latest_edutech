import datetime
from django.db import models
from students.models import Students

class UniqueIds(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    dateCreated = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = 'uniqueids'
# Create your models here.

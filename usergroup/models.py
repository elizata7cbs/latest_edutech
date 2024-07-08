# Create your models here.
from django.db import models


class UserGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    groupID = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    dateCreated = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=1)

    def _str_(self):
        return self.name

        class Meta:
            db_table = 'usergroup'
from django.db import models

from schools.models import Schools
from students.models import Students


# Create your models here.


class StudentsSchools(models.Model):
    id = models.AutoField(primary_key=True)
    schoolID = models.ForeignKey(Schools, on_delete=models.CASCADE)
    studentID = models.ForeignKey(Students, on_delete=models.CASCADE)
    dateCreated = models.DateField(auto_now_add=True)

    def _str_(self):
        return f"{self.schoolID.schoolName} - {self.studentID.studentName}"


class Meta:
    db_table = 'studentsparents'

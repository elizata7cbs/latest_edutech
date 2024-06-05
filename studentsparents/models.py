from django.db import models
from parents.models import Parents
from students.models import Students


class StudentsParents(models.Model):
    id = models.AutoField(primary_key=True)
    parentIdno = models.ForeignKey(Parents, on_delete=models.CASCADE)
    studentID = models.ForeignKey(Students, on_delete=models.CASCADE)
    dateCreated = models.DateField(auto_now_add=True)

    def _str_(self):
        return f"{self.parentIdno.parentName} - {self.studentID.studentName}"


class Meta:
    db_table = 'studentsparents'  # Optional: specify the database table name
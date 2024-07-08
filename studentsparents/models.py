from django.db import models
from parents.models import Parents
from students.models import Students
import requests

class StudentsParents(models.Model):
    id = models.AutoField(primary_key=True)
    parentID = models.ForeignKey(Parents, on_delete=models.CASCADE)
    studentID = models.ForeignKey(Students, on_delete=models.CASCADE)
    dateCreated = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.parentID.parentName} - {self.studentID.studentName}"

    class Meta:
        db_table = 'studentsparents'  # Optional: specify the database table name

    def get_balance(self):
        try:
            balance_response = requests.get(f"http://payfeeapp/api/recordtransaction?parent_id={self.parentID.id}")
            if balance_response.status_code == 200:
                balance_data = balance_response.json()
                return balance_data.get('balance', 0.0)
            else:
                return 0.0
        except requests.RequestException:
            return 0.0  # Handle any request exceptions

import datetime
from django.db import models


class Students(models.Model):
    id = models.AutoField(primary_key=True)
    uniqueId = models.CharField(max_length=50)
    admNumber = models.CharField(max_length=255)
    schoolCode = models.CharField(max_length=50)
    firstName = models.CharField(max_length=255)
    middleName = models.CharField(max_length=255, null=True)
    lastName = models.CharField(max_length=255)
    studentGender = models.CharField(max_length=255)
    deleteFlag = models.CharField(max_length=1, default="N")
    transferFlag = models.CharField(max_length=1, default="Y")
    dob = models.DateField()  # Changed from CharField to DateField
    dateOfAdmission = models.DateField()  # Added this line
    healthStatus = models.CharField(max_length=255)
    grade = models.IntegerField()
    stream = models.CharField(max_length=255)
    schoolStatus = models.CharField(max_length=255)
    dormitory = models.CharField(max_length=255)
    status = models.IntegerField(default=1)
    parentIdno = models.IntegerField()
    schoolID = models.IntegerField()
    urls = models.CharField(max_length=500)


    def __str__(self):
        return f"{self.firstName} {self.middleName} {self.lastName}"

    class Meta:
        db_table = 'students'  # Optional: specify the database table name


class StudentAccount(models.Model):
    student = models.OneToOneField(Students, on_delete=models.CASCADE)
    debit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField(auto_now_add=True)

    @property
    def balance(self):
        # Calculate the balance
        return self.debit - self.credit

    def __str__(self):
        # Return a string representation of the object
        return f"Student: {self.student}, Balance: {self.balance}"


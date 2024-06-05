from django.db import models

# Create your models here.
from django.db import models

class SystemInfo(models.Model):
    school_name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    contact_email = models.EmailField(max_length=100)
    contact_phone = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    # current_session = models.CharField(max_length=20)
    school_type = models.CharField(max_length=20, choices=[('Preprimary', 'Preprimary'), ('Primary', 'Primary'), ('Junior Secondary', 'Junior Secondary'), ('Senior Secondary', 'Senior Secondary'), ('Tertiary', 'Tertiary')])  # Changed this line

    def str(self):
        return self.school_name

    class Meta:
        db_table = 'system_info'
        verbose_name_plural = 'System Information'
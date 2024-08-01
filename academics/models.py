from django.db import models
from django.core.exceptions import ValidationError


class AcademicYear(models.Model):
    academic_year_name = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    GRADE_CHOICES = [
        ('1', 'Grade 1'),
        ('2', 'Grade 2'),
        ('3', 'Grade 3'),
        # Add other grades as necessary
    ]
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES)

    def __str__(self):
        return self.academic_year_name

    def clean(self):
        # Ensure start_date is before end_date
        if self.start_date >= self.end_date:
            raise ValidationError('Start date must be before end date')

        # Ensure no overlapping academic years
        if AcademicYear.objects.filter(
            start_date__lt=self.end_date,
            end_date__gt=self.start_date,
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Academic year dates overlap with another academic year')

    def save(self, *args, **kwargs):
        self.clean()
        super(AcademicYear, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Academic Year"
        verbose_name_plural = "Academic Years"

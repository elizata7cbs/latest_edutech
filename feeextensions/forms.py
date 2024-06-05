from django import forms
from .models import FeeExtensions
from django.forms import DateInput
from utils.Helpers import calculate_next_due_date


class FeeExtensionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the order of form fields
        self.fields['student_unique_id'].widget.attrs.update({'autofocus': 'autofocus'})  # Set focus on this field
        self.fields['school_code'].widget.attrs.update({'readonly': 'readonly'})  # Make school code field readonly

        # Auto-fill dueDate using calculate_due_date() from helpers.py
        if 'start_date' in self.initial and 'frequency' in self.initial:
            start_date = self.initial['start_date']
            frequency = self.initial['frequency']
            self.fields['dueDate'].initial = calculate_next_due_date(start_date, start_date, frequency)

        # Validate student_unique_id and auto-fill student and user fields
        if 'data' in kwargs:
            student_unique_id = kwargs['data'].get('student_unique_id', None)
            if student_unique_id:
                # Query the database to get student name based on student_unique_id
                student_name = "John Doe"  # Sample student name retrieved from the database
                self.fields['student'].initial = student_name

    class Meta:
        model = FeeExtensions
        fields = ['user', 'student', 'student_unique_id', 'feecategory', 'dueDate', 'school_code', 'start_date', 'end_date', 'frequency', 'amount', 'last_reminder_sent', 'reminder_frequency']
        widgets = {
            'start_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'}),
        }

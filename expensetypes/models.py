from django.db import models
from django.core.exceptions import ValidationError


class ExpenseTypes(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    hierarchical_code = models.CharField(max_length=10, unique=True, editable=False, default='')

    class Meta:
        db_table = 'expensetypes'

    def save(self, *args, **kwargs):
        if not self.hierarchical_code:
            existing_expense_types = ExpenseTypes.objects.filter(name=self.name)
            if existing_expense_types.exists():
                # If expense types with the same name exist, set hierarchical code based on the first one
                hierarchical_code = existing_expense_types.first().hierarchical_code
            else:
                last_type = ExpenseTypes.objects.order_by('-id').first()
                if not last_type:
                    new_code = "001"
                else:
                    last_code = last_type.hierarchical_code
                    number = int(last_code) + 1
                    new_code = f"{number:03d}"
                hierarchical_code = new_code

            self.hierarchical_code = hierarchical_code

        try:
            super().save(*args, **kwargs)
        except ValidationError as e:
            if 'name' in e.message_dict and 'unique' in e.message_dict['name']:
                # Handle uniqueness error for name field
                raise ValidationError({'expensetypes': {'name': ['Expense types with this name already exist.']}})
            else:
                raise  # Re-raise the original ValidationError if it's not related to the name field

    def __str__(self):
        return self.name

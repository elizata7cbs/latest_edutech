from django.db import models
from django.contrib.auth.models import User


COUNTRY_CHOICES = (
    ('Kenya', 'Kenya'),
    ('Uganda', 'Uganda'),
    ('Tanzania', 'Tanzania'),
    ('Democratic Republic of the Congo', 'Democratic Republic of the Congo'),
    ('Rwanda', 'Rwanda'),
    ('South Sudan', 'South Sudan'),
    ('Ethiopia', 'Ethiopia'),
)

COUNTRY_CODES = (
    ('KE', 'KE'),
    ('UG', 'UG'),
    ('TZ', 'TZ'),
    ('DRC', 'DRC'),
    ('RW', 'RW'),
    ('SS', 'SS'),
    ('ET', 'ET'),
)

PHONE_NUMBER_COUNTRY_CODES = (
    ('254', '254'),
    ('256', '256'),
    ('255', '255'),
    ('243', '243'),
    ('250', '250'),
    ('211', '211'),
    ('251', '251'),
)

CURRENCY_CHOICES = (
    ('KES', 'Kenyan Shilling'),
    ('UGX', 'Ugandan Shilling'),
    ('TZS', 'Tanzanian Shilling'),
    ('CDF', 'Congolese Franc'),
    ('RWF', 'Rwandan Franc'),
    ('USD', 'US Dollar'),
    ('EUR', 'Euro'),
    ('SSP', 'South Sudanese Pound'),
    ('ETB', 'Ethiopian Birr'),
)

class Schools(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-generated primary key (internal use)
    name = models.CharField(max_length=255, unique=True)  # Ensure unique school names
    school_code = models.CharField(max_length=255, blank=True, null=True)
    # Address fields
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES, verbose_name="Country", default='Kenya')
    country_code = models.CharField(max_length=3, choices=COUNTRY_CODES, verbose_name="Country Code", default='KE')
    county = models.CharField(max_length=100)
    sub_county = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=255, blank=True)
    street_address = models.TextField(blank=True)
    postal_code = models.CharField(max_length=20, blank=True)  # Optional, depending on postal systems

    # Contact details
    phone_number1 = models.CharField(max_length=20)
    phone_number2 = models.CharField(max_length=20)
    phone_number_country_code = models.CharField(max_length=3, choices=PHONE_NUMBER_COUNTRY_CODES, verbose_name="Phone Number Country Code", default='254')
    email_address = models.EmailField()
    website = models.URLField(blank=True)

    # Additional fields specific to Kenyan/East African schools
    registration_number = models.CharField(max_length=20, blank=True)  # For government-registered schools
    school_type = models.CharField(max_length=50, choices=(  # No default choice
        ('PRE-PRIMARY', 'pre-primary'),
        ('PRIMARY', 'Primary'),
        ('SECONDARY', 'Secondary'),
        ('COLLEGE', 'college'),
        ('UNIVERSITY', 'university'),
        ('OTHER', 'Other'),
    ), blank=True)  # Allow null value
    boarding_status = models.CharField(max_length=20, choices=(  # No default choice
        ('DAY', 'Day'),
        ('BOARDING', 'Boarding'),
        ('MIXED', 'Mixed'),
    ), blank=True)  # Allow null value
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, verbose_name="Currency", default='KES')
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)  # School logo
    date_created = models.DateField(auto_now_add=True)  # Date school record created

    def __str__(self):
        return self.name

class SchoolAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='school_admin')
    school = models.ForeignKey(Schools, on_delete=models.CASCADE, related_name='admin')
    title = models.CharField(max_length=10, default='Mr', choices=(
        ('MR', 'Mr'),
        ('MRS', 'Mrs'),
        ('MISS', 'Miss'),
        ('DR', 'Dr'),
        ('PROF', 'Professor'),
        ('MS', 'Ms'),
        ('MX', 'Mx'),
        ('REV', 'Reverend'),
        ('SIR', 'Sir'),
        ('MADAM', 'Madam'),
    ))
    designation = models.CharField(max_length=50, default='OWNER', choices=(
        ('OWNER', 'School Owner'),
        ('DIR', 'School Director'),
        ('FIN', 'Finance Admin'),
        ('HEAD', 'Headteacher'),
        ('OTHER', 'Other'),
    ))

    def __str__(self):
        return self.user.username

class Branch(models.Model):
    school = models.ForeignKey(Schools, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES, verbose_name="Country", default='Kenya')
    country_code = models.CharField(max_length=3, choices=COUNTRY_CODES, verbose_name="Country Code", default='DRC')
    county = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)

    # Contact details (consider what's most relevant)
    phone_number = models.CharField(max_length=20)
    phone_number_country_code = models.CharField(max_length=3, choices=PHONE_NUMBER_COUNTRY_CODES, verbose_name="Phone Number Country Code", default='254')
    email = models.EmailField(blank=True)

    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

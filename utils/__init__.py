from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.db import connection

from edutech_payment_engine.settings import *
from users.models import CustomUser
from schools.models import Schools  # Ensure this import matches your project structure
import sys
from parents.models import Parents
from students.models import Students

if 'runserver' in sys.argv:
    required_groups = ['admin', 'superuser', 'accountant']
    print("Creating user groups")
    for group_name in required_groups:
        if not Group.objects.filter(name=group_name).exists():
            Group.objects.create(name=group_name)
    # Check and create parent if it does not exist
    if not Parents.objects.exists():
        print("Creating parent")
        parent = Parents.objects.create(
            first_name='John Doe',
            last_name='Smith',
            email='john.doe@example.com',
            phone_number='+254712345678',
            parentIdno='12345678')
    # Check and create student if it does not exist
    if not Students.objects.exists():
        print("Creating student")
        student = Students.objects.create(
            admNumber='1234',
            firstName='Jane',
            middleName='lee',
            lastName='Zoe',
            studentGender='Female',
            dob='2024-7-18',
            upiNumber='asdf3456',
            grade='7',
            stream='Red',
            parentID='1')
    # Check and create school if it does not exist
    if not Schools.objects.exists():
        print("Creating dummy school")
        school = Schools.objects.create(
            name=SCHOOL_NAME,
            school_code=SCHOOL_CODE,
            country=COUNTRY,
            country_code=COUNTRY_CODE,
            county=COUNTY,
            sub_county=SUB_COUNTY,
            city=CITY,
            street_address=STREET_ADDRESS,
            postal_code=POSTAL_CODE,
            phone_number1=PHONE_NUMBER1,
            phone_number2=PHONE_NUMBER2,
            phone_number_country_code=PHONE_NUMBER_COUNTRY_CODE,
            email_address=EMAIL_ADDRESS,
            website=WEBSITE,
            registration_number=REGISTRATION_NUMBER,
            school_type=SCHOOL_TYPE,
            boarding_status=BOARDING_STATUS,
            currency=CURRENCY,
        )

    # Check and create superuser if it does not exist
    if not CustomUser.objects.filter(is_superuser=True).exists():
        print("Creating dummy User")
        school = Schools.objects.get(id=1)
        group = Group.objects.get(name='superuser')
        user = CustomUser.objects.create(
            first_name=SUPERUSER_FIRST_NAME,
            last_name=SUPERUSER_LAST_NAME,
            username=SUPERUSER_USERNAME,
            is_superuser=True,
            is_staff=True,
            is_active=True,
            schools=school,
            email=SUPERUSER_EMAIL,
            usergroup=group,
            address="N/A",
            is_verified=True,
            phone_number=SUPERUSER_PHONE_NUMBER,
            password=make_password(SUPERUSER_PASSWORD),
        )
        user.groups.add(group)
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print(f"Username: {SUPERUSER_USERNAME} Password: {SUPERUSER_PASSWORD}")
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")






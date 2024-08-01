# from django.contrib.auth.models import Permission
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
#
#
# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)
#         token['email'] = user.email
#         # token['user_category'] = user.user_category.name if user.user_category else None
#         # token['is_verified'] = user.is_verified
#         # token['first_name'] = user.first_name
#         # token['last_name'] = user.last_name
#         #
#         # # # Get the name of the first group the user belongs to
#         # group_name = user.groups.first().name if user.groups.first() else None
#         #
#         # # Fetch permissions based on user's group
#         # if group_name:
#         #     auth_perms = Permission.objects.filter(group__name=group_name)
#         #     # Serialize permissions
#         #     permissions_data = [{"name": perm.name, "codename": perm.codename} for perm in auth_perms]
#         #     token["permissions"] = permissions_data
#
#         return token
#
from django.contrib.auth.models import Permission
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from schools.models import Schools

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add user details to the token
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['middle_name'] = user.middle_name
        token['gender'] = user.gender
        token['date_of_birth'] = user.date_of_birth.isoformat() if user.date_of_birth else None
        token['address'] = user.address
        token['nationality'] = user.nationality
        token['phone_number'] = user.phone_number
        token['is_verified'] = user.is_verified
        token['first_login'] = user.is_verified

        # Add school details if the user is associated with a school
        if user.schools:
            token['school'] = {
                'name': user.schools.name,
                'school_code': user.schools.school_code,
                'country': user.schools.country,
                'country_code': user.schools.country_code,
                'county': user.schools.county,
                'sub_county': user.schools.sub_county,
                'city': user.schools.city,
                'street_address': user.schools.street_address,
                'postal_code': user.schools.postal_code,
                'phone_number1': user.schools.phone_number1,
                'phone_number2': user.schools.phone_number2,
                'phone_number_country_code': user.schools.phone_number_country_code,
                'email_address': user.schools.email_address,
                'website': user.schools.website,
                'registration_number': user.schools.registration_number,
                'school_type': user.schools.school_type,
                'boarding_status': user.schools.boarding_status,
                'currency': user.schools.currency,
                'date_created': user.schools.date_created.isoformat() if user.schools.date_created else None,
            }
        else:
            token['school'] = None

        # Add permissions based on user's group
        if user.groups.exists():
            group = user.groups.first()
            token['group_name'] = group.name
            auth_perms = Permission.objects.filter(group=group)
            permissions_data = [{"name": perm.name, "codename": perm.codename} for perm in auth_perms]
            token["permissions"] = permissions_data
        else:
            token['group_name'] = None
            token["permissions"] = []

        return token

import random
import string
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from users.models import CustomUser  # Adjust the import to match your app's structure
from utils.Helpers import Helpers  # Import your helper class

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser  # Replace with your user model
        fields = ['first_name', 'username', 'middle_name', 'last_name', 'gender', 'address', 'nationality', 'email',
                  'schools', 'usergroup', 'date_of_birth']

    def create(self, validated_data):
        helpers = Helpers()  # Instantiate the Helpers class

        # Extract the email to use as the password
        email = validated_data.get('email')
        if not email:
            raise serializers.ValidationError("Email is required to create a user.")

        # Use the email as the password
        plain_password = email

        # Print the plain password for debugging
        print(f"Generated password: {plain_password}")

        # Generate username by concatenating first name and last name with a dot
        first_name = validated_data.get('first_name', '').capitalize()
        last_name = validated_data.get('last_name', '').capitalize()
        username = f"{first_name}.{last_name}"

        # Ensure username is unique
        if CustomUser.objects.filter(username=username).exists():
            count = CustomUser.objects.filter(username__startswith=username).count()
            username = f"{username}{count+1}"

        # Set the generated username in the validated_data
        validated_data['username'] = username

        # Hash the plain password (email)
        validated_data['password'] = make_password(plain_password)

        # Create the user with the hashed password and generated username
        user = super(CustomUserSerializer, self).create(validated_data)

        # Send the email to the user's email address
        if email:
            helpers.send_generated_password(first_name, username, plain_password, email)

        return user

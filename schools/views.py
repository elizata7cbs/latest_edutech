from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Schools
from .serializers import SchoolsSerializer
from utils.ApiResponse import ApiResponse
from utils.Helpers import Helpers  # Import Helpers class

class SchoolsViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and manipulating school instances.
    Provides `list`, `retrieve`, `update`, and `destroy` actions.
    """
    queryset = Schools.objects.all()
    serializer_class = SchoolsSerializer

    helpers = Helpers()

    def create(self, request, *args, **kwargs):
        response = ApiResponse()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Generate a unique school code
            name = serializer.validated_data.get('name')
            school_code = self.helpers.generateSchoolCode(name)

            # Save the school code in the serializer data
            serializer.validated_data['school_code'] = school_code

            # Save the school with the generated code
            new_school = serializer.save()

            response.setStatusCode(status.HTTP_201_CREATED)
            response.setMessage("School created")
            response.setEntity(serializer.data)
            return Response(response.toDict(), status=response.status)
        else:
            print("Serializer Errors:", serializer.errors)  # Debug statement to print serializer errors
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Please fill in your details correctly", "errors": serializer.errors,
                             "status": status_code}, status=status_code)

    def update(self, request, *args, **kwargs):
        """
        Override the `update` method to handle potential school code updates (optional).
        """
        school = self.get_object()

        # Check if the request data contains a 'school_code' field (optional)
        if 'school_code' in request.data:
            # Validate the requested school code using helper function
            validation_result = Helpers().validate_school_code(request.data['school_code'])

            if not validation_result:
                return Response({"message": "Invalid school code format or already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # Update other school fields using the serializer
        school_serializer = SchoolsSerializer(school, data=request.data, partial=True)
        if school_serializer.is_valid():
            school_serializer.save()
            response = ApiResponse()
            response.setStatusCode(status.HTTP_200_OK)
            response.setMessage("School Updated Successfully")
            return Response(response.toDict(), status=response.status)
        else:
            return Response(school_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        school = self.get_object()
        school.is_active = False  # Deactivate the school
        school.save()
        response = ApiResponse()
        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("School deactivated Successfully")
        return Response(response.toDict(), status=response.status)
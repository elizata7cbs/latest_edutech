from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework_jwt.utils import jwt_encode_handler
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from edutech_payment_engine.settings import inProd
from authuser.models import OTP
from authuser.resetPassSerializer import ResetPassSerializer
from authuser.sentOTPSerializer import sentOTPSerializer
from authuser.serializers import AuthUserSerializer
from authuser.validateOTPSerializer import ValidateOTPSerializer
from users.models import CustomUser
from users.serializers import CustomUserSerializer
from utils.ApiResponse import ApiResponse
from utils.Helpers import Helpers
from django.utils import timezone
from datetime import datetime


class AuthUSer(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = AuthUserSerializer

    def get_serializer_class(self):
        if self.action == 'sendOTP':
            return sentOTPSerializer
        elif self.action == "verifyOTP":
            return ValidateOTPSerializer
        elif self.action == "resetpassword":
            return ResetPassSerializer
        return AuthUserSerializer

    @action(detail=False, methods=['POST'])
    def authUser(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        helpers = Helpers()
        helpers.log(request)
        if username and password:
            try:
                user = CustomUser.objects.get(Q(username=username) | Q(email=username))
                if user.check_password(password):
                    if user.check_password(password):
                        if not user.is_verified:
                            response = ApiResponse()
                            response.setStatusCode(status.HTTP_401_UNAUTHORIZED)
                            response.setMessage("Account is not verified")
                            return Response(response.toDict(), status=200)
                    serializer = CustomUserSerializer(user)
                    data = serializer.data
                    otp = helpers.generateotp()
                    email = serializer.data.get("email")
                    name = serializer.data.get("name")
                    saveOtp = helpers.saveotp(otp, email)
                    sent = helpers.otp(name, otp, email)
                    print("Use OTP: " + otp)
                    user_permissions = user.user_permissions.all()
                    roles = [permission.name for permission in user_permissions]
                    data['roles'] = roles
                    response = ApiResponse()
                    response.setStatusCode(status.HTTP_200_OK)
                    response.setMessage("Check for an OTP on your email")
                    response.setEntity(data)
                    return Response(response.toDict(), status=response.status)
                else:
                    response = ApiResponse()
                    response.setStatusCode(status.HTTP_400_BAD_REQUEST)
                    response.setMessage("Incorrect login credentials")
                    return Response(response.toDict(), status=200)
            except CustomUser.DoesNotExist:

                response = ApiResponse()
                response.setStatusCode(status.HTTP_400_BAD_REQUEST)
                response.setMessage("Incorrect login credentials")
                return Response(response.toDict(), status=200)
        else:
            response = ApiResponse()
            response.setStatusCode(400)
            response.setMessage("Email and password are required")
            return Response(response.toDict(), status=response.status)

    @action(detail=False, methods=['POST'])
    def authParent(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        helpers = Helpers()
        helpers.log(request)
        if username and password:
            try:
                user = CustomUser.objects.get(Q(username=username) | Q(email=username))
                if user.check_password(password):
                    if user.check_password(password):
                        if not user.is_verified:
                            response = ApiResponse()
                            response.setStatusCode(status.HTTP_401_UNAUTHORIZED)
                            response.setMessage("Account is not verified")
                            return Response(response.toDict(), status=200)
                    serializer = CustomUserSerializer(user)
                    data = serializer.data
                    otp = helpers.generateotp()
                    email = serializer.data.get("email")
                    name = serializer.data.get("name")
                    saveOtp = helpers.saveotp(otp, email)
                    sent = helpers.otp(name, otp, email)
                    print("Use OTP: " + otp)
                    user_permissions = user.user_permissions.all()
                    roles = [permission.name for permission in user_permissions]
                    data['roles'] = roles
                    response = ApiResponse()
                    response.setStatusCode(status.HTTP_200_OK)
                    response.setMessage("Check for an OTP on your email")
                    response.setEntity(data)
                    return Response(response.toDict(), status=response.status)
                else:
                    response = ApiResponse()
                    response.setStatusCode(status.HTTP_400_BAD_REQUEST)
                    response.setMessage("Incorrect login credentials")
                    return Response(response.toDict(), status=200)
            except CustomUser.DoesNotExist:

                response = ApiResponse()
                response.setStatusCode(status.HTTP_400_BAD_REQUEST)
                response.setMessage("Incorrect login credentials")
                return Response(response.toDict(), status=200)
        else:
            response = ApiResponse()
            response.setStatusCode(400)
            response.setMessage("Email and password are required")
            return Response(response.toDict(), status=response.status)

    @action(detail=False, methods=['POST'])
    def sendOTP(self, request):
        response = ApiResponse()
        helpers = Helpers()
        helpers.log(request)
        serializer = sentOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            print(email)
            if email:
                try:
                    user = CustomUser.objects.get(email=email)
                    user_serializer = CustomUserSerializer(user)
                    name = user_serializer.data.get('name')
                    otp = helpers.generateotp()
                    try:
                        saveOtp = helpers.saveotp(otp, email)
                        if inProd:
                            sent = helpers.otp(name, otp, email)
                            if sent == 1:
                                print("Sent OTP: ", otp)
                                response.setMessage("An OTP was sent to your Email.")
                                response.setStatusCode(200)
                                return Response(response.toDict(), 200)
                            else:
                                response.setMessage("Failed to send Email")
                                response.setStatusCode(401)
                                return Response(response.toDict(), 200)

                        print("Sent OTP: ", otp)
                        response.setMessage("An OTP was sent to your Email.")
                        response.setStatusCode(200)
                        return Response(response.toDict(), 200)
                    except Exception as e:
                        response.setMessage(f"Error sending email: {str(e)}")
                        response.setStatusCode(401)
                        return Response(response.toDict(), 200)
                except CustomUser.DoesNotExist:
                    response.setMessage("No record found with this Email")
                    response.setStatusCode(404)
                    return Response(response.toDict(), 200)
            else:
                status_code = status.HTTP_400_BAD_REQUEST
                return Response({"message": "Email parameter is required", "status": status_code})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def verifyOTP(self, request):
        response = ApiResponse()
        helpers = Helpers()
        helpers.log(request)
        serializer = ValidateOTPSerializer(data=request.data)
        if serializer.is_valid():
            otp = serializer.validated_data.get('otp')
            email = serializer.validated_data.get('email')
            try:
                existing_otp = OTP.objects.filter(email=email).last()
                if existing_otp.otp == otp:
                    current_time = timezone.now()
                    expirydate_str_without_timezone = existing_otp.expirydate.rsplit('.', 1)[0]
                    expiry_time = datetime.strptime(expirydate_str_without_timezone, "%Y-%m-%d %H:%M:%S")
                    expiry_time = timezone.make_aware(expiry_time, timezone.utc)
                    if current_time <= expiry_time:
                        response.setMessage("OTP validated")
                        user = CustomUser.objects.get(email=email)
                        print(user.username)
                        refresh = RefreshToken.for_user(user)
                        access = AccessToken.for_user(user)
                        access['email'] = user.email
                        refresh['email'] = user.email
                        access['role'] = user.usergroup.name

                        response.setStatusCode(200)
                        auth = {
                            'access_token': str(access),
                            'refresh_token': str(refresh),
                            'token_type': 'bearer',
                            'expires_in': 3600,

                        }
                        response.setEntity(auth)
                        return Response(response.toDict(), 200)
                    else:
                        response.setMessage("OTP has expired")
                        response.setStatusCode(400)
                        return Response(response.toDict(), 200)
                else:
                    response.setMessage("Invalid OTP")
                    response.setStatusCode(400)
                    return Response(response.toDict(), 200)
            except OTP.DoesNotExist:
                response.setMessage("OTP does not exist for the provided email")
                response.setStatusCode(404)
                return Response(response.toDict(), 200)

        response.setMessage("Invalid data provided")
        response.setStatusCode(400)
        return Response(response.toDict(), 200)

    def generate_jwt_token(self, user):
        payload = {
            'user_id': user.id,
        }
        token = jwt_encode_handler(payload)
        return token

    @action(detail=False, methods=['POST'])
    def resetpassword(self, request):
        response = ApiResponse()
        helpers = Helpers()
        helpers.log(request)
        serializer = ResetPassSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data.get('password')
            email = serializer.validated_data.get('email')
            try:
                existingUser = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                response.setStatusCode(404)
                response.setMessage("User not found")
                return Response(response.toDict(), 200)

            existingUser.set_password(password)
            existingUser.save()
            response.setStatusCode(200)
            response.setMessage("Password Updated")
            return Response(response.toDict(), 200)
        else:
            response.setStatusCode(400)
            response.setMessage("Invalid data")
            response.setEntity(serializer.errors)
            return Response(response.toDict(), 200)

import base64
import json
from datetime import datetime

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from edutech_payment_engine.settings import *
from utils.ApiResponse import ApiResponse


# Create your views here.
class Mpesa(viewsets.ViewSet):

    def lipa_na_mpesa(self, request, *args, **kwargs):
        i = ApiResponse()
        phone = kwargs['phone']
        amount = kwargs['amount']
        response = self.Push(phone, amount)  # Call Push method directly
        print(response)
        i.setMessage("Push was sent")
        i.setEntity(response)
        i.setStatusCode(200)
        return Response(i.toDict(), 200)

    @staticmethod
    def Push(phone, amount):  # Make Push method static
        # Set the timezone

        # Define parameters
        PartyA = phone
        AccountReference = '2255'
        TransactionDesc = 'Test Payment'
        Amount = amount

        # Get the timestamp
        Timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

        # Generate the password
        Password = base64.b64encode((BSS_SHORT_CODE + PASS_KEY + Timestamp).encode()).decode()

        # Get the access token
        headers = {'Content-Type': 'application/json; charset=utf8'}
        auth = (CONSUMER_KEY, CONSUMER_SECRET)
        response = requests.get(ACCESS_TOKEN_URL, headers=headers, auth=auth)
        access_token = response.json().get('access_token')

        # Prepare the request data
        data = {
            'BusinessShortCode': BSS_SHORT_CODE,
            'Password': Password,
            'Timestamp': Timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': Amount,
            'PartyA': PartyA,
            'PartyB': BSS_SHORT_CODE,
            'PhoneNumber': PartyA,
            'CallBackURL': 'https://84e4-102-220-12-50.ngrok-free.app/api/v1/mpesa/mpesa_callback/',
            'AccountReference': AccountReference,
            'TransactionDesc': TransactionDesc
        }

        # Make the STK Push request
        stk_response = requests.post(INITIATE_URL, json=data, headers={'Authorization': 'Bearer ' + access_token})

        return stk_response.text

@csrf_exempt
@require_POST
@api_view(['POST'])
def call_back_url(request):
    try:
        # Parse the JSON data posted to the callback URL
        mpesa_response = json.loads(request.body)

        # Log the response to a file
        log_file = "M_PESAConfirmationResponse.txt"
        with open(log_file, "a") as log:
            log.write(json.dumps(mpesa_response) + "\n")

        print(mpesa_response)

        # Extract the ResultCode
        result_code = mpesa_response['Body']['stkCallback']['ResultCode']

        if result_code == 0:
            # Extract additional information from the CallbackMetadata
            callback_metadata = mpesa_response['Body']['stkCallback']['CallbackMetadata']['Item']

            # Initialize variables to store the extracted data
            mpesa_receipt_number = transaction_date = phone_number = amount = None

            # Iterate through the metadata to extract the required fields
            for item in callback_metadata:
                if item['Name'] == 'MpesaReceiptNumber':
                    mpesa_receipt_number = item['Value']
                elif item['Name'] == 'TransactionDate':
                    transaction_date = item['Value']
                elif item['Name'] == 'PhoneNumber':
                    phone_number = item['Value']
                elif item['Name'] == 'Amount':
                    amount = item['Value']

            # Print the extracted values
            print("MpesaReceiptNumber:", mpesa_receipt_number)
            print("TransactionDate:", transaction_date)
            print("PhoneNumber:", phone_number)
            print("Amount:", amount)

            # Return the success response
            response = {
                "ResultCode": 0,
                "ResultDesc": "Confirmation Received Successfully"
            }
            print(response)

            return JsonResponse(response, status=200)
        else:
            # Return a response indicating that the transaction failed
            response = {
                "ResultCode": result_code,
                "ResultDesc": "Transaction failed"
            }
            print(response)
            return JsonResponse(response, status=400)

    except json.JSONDecodeError:
        print("Invalid JSON data")
        return JsonResponse({"message": "Invalid JSON data"}, status=400)
    except KeyError as e:
        print(f"Missing key in JSON data: {e}")
        return JsonResponse({"message": f"Missing key in JSON data: {e}"}, status=400)
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)

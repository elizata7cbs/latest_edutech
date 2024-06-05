import base64
from datetime import datetime

import requests
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
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

    @csrf_exempt
    def mpesa_callback(self, request):  # Update method signature to accept request
        callback_data = request.data

        # Check if the necessary keys are present in the callback data
        if 'Body' in callback_data and 'stkCallback' in callback_data['Body']:
            # Extract relevant data from callback_data
            stk_callback = callback_data['Body']['stkCallback']
            result_code = stk_callback.get('ResultCode', None)
            if result_code is not None:
                # Check the result code
                if result_code != 0:
                    # If the result code is not 0, there was an error
                    error_message = stk_callback.get('ResultDesc', '')
                    response_data = {'ResultCode': result_code, 'ResultDesc': error_message}
                    return Response(response_data)
                print(request.data)

                # If the result code is 0, the transaction was completed
                callback_metadata = stk_callback.get('CallbackMetadata', {})
                amount = None
                phone_number = None
                for item in callback_metadata.get('Item', []):
                    if item['Name'] == 'Amount':
                        amount = item['Value']
                    elif item['Name'] == 'PhoneNumber':
                        phone_number = item['Value']

                # Return a success response to the M-Pesa server
                response_data = {'ResultCode': result_code, 'ResultDesc': 'Success'}
                return Response(response_data)
        # If the necessary keys are not present, return a bad request response
        return Response({'error': 'Invalid callback data'}, status=400)

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
            'CallBackURL': 'https://3db4-102-210-244-74.ngrok-free.app/lipa_na_mpesa',
            'AccountReference': AccountReference,
            'TransactionDesc': TransactionDesc
        }

        # Make the STK Push request
        stk_response = requests.post(INITIATE_URL, json=data, headers={'Authorization': 'Bearer ' + access_token})

        return stk_response.text

from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.response import Response

import suppliers
from suppliers.models import Suppliers, SuppliersAccount
from suppliers.serializers import SuppliersSerializers
from utils.ApiResponse import ApiResponse
from utils.Helpers import Helpers


# from rest_framework.permissions import IsAuthenticated
# from rest_framework.authentication import SessionAuthentication, BasicAuthentication
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class SuppliersView(viewsets.ModelViewSet):
    queryset = Suppliers.objects.all()
    serializer_class = SuppliersSerializers

    # authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def listsupplier(self, request, *args, **kwargs):
        response = ApiResponse()
        suppliers_data = Suppliers.objects.all().values()
        response.setStatusCode(status.HTTP_200_OK)
        response.setMessage("Found")
        response.setEntity(list(suppliers_data))
        return Response(response.toDict(), status=response.status)

    def list_suppliers_account(self, request, *args, **kwargs):
        response = ApiResponse()
        helper = Helpers()

        try:
            # Retrieve all supplier accounts along with their associated suppliers
            suppliers_accounts = SuppliersAccount.objects.select_related('supplier').all()

            # Check if any supplier accounts exist
            if suppliers_accounts.exists():
                # Construct account information for each supplier
                suppliers_accounts_info = []
                for supplier_account in suppliers_accounts:
                    # Retrieve the supplier's information associated with the account
                    supplier = supplier_account.supplier

                    # Construct account information with additional fields
                    account_info = {
                        'supplier_id': supplier.id,
                        'business_name': supplier.businessName,
                        'debit': supplier_account.debit,
                        'credit': supplier_account.credit,
                        'balance': supplier_account.balance,
                    }
                    suppliers_accounts_info.append(account_info)

                response.setStatusCode(status.HTTP_200_OK)
                response.setMessage("Found")
                response.setEntity(suppliers_accounts_info)
            else:
                # No supplier accounts found
                response.setStatusCode(status.HTTP_404_NOT_FOUND)
                response.setMessage("Supplier accounts not found")

            return Response(response.toDict(), status=response.status)

        except Exception as e:
            # Handle any unexpected exceptions
            response.setStatusCode(status.HTTP_500_INTERNAL_SERVER_ERROR)
            response.setMessage("Internal Server Error")
            return Response(response.toDict(), status=response.status)

    def create(self, request, *args, **kwargs):
        response = ApiResponse()
        suppliers_data = SuppliersSerializers(data=request.data)
        if suppliers_data.is_valid():
            check_id = request.data.get("supplierId")
            existing_supplier = Suppliers.objects.filter(id=check_id).first()
            if existing_supplier:
                status_code = status.HTTP_400_BAD_REQUEST
                return Response({"message": "Supplier already exists.", "status": status_code}, status_code)
            suppliers_data.save()
            response.setStatusCode(status.HTTP_201_CREATED)
            response.setMessage("Supplier created")
            response.setEntity(request.data)
            return Response(response.toDict(), status=response.status)
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Please fill in the details correctly.", "status": status_code}, status_code)

    def destroy(self, request, *args, **kwargs):
        supplier_data = Suppliers.objects.filter(id=kwargs['pk'])
        if supplier_data:
            supplier_data.delete()
            status_code = status.HTTP_200_OK
            return Response({"message": "Supplier deleted successfully", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Supplier data not found", "status": status_code})

    def update(self, request, *args, **kwargs):
        supplier_details = Suppliers.objects.filter(id=kwargs['pk']).first()
        if supplier_details:
            suppliers_serializer_data = SuppliersSerializers(
                supplier_details, data=request.data, partial=True)
            if suppliers_serializer_data.is_valid():
                suppliers_serializer_data.save()
                status_code = status.HTTP_201_CREATED
                return Response({"message": "Supplier updated successfully", "status": status_code})
            else:
                status_code = status.HTTP_400_BAD_REQUEST
                return Response({"message": "Supplier data not found", "status": status_code})
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            return Response({"message": "Supplier data not found", "status": status_code})

    def filter_suppliers(self, request):
        fields_to_filter = ['id', 'businessName', 'supplierNO', 'dateCreated']
        filter_criteria = {}

        for field in fields_to_filter:
            value = request.GET.get(field)
            if value:
                filter_criteria[field] = value

        filtered_suppliers = Suppliers.objects.filter(**filter_criteria)
        suppliers_data = list(filtered_suppliers.values())

        return JsonResponse(dict(suppliers=suppliers_data))

    # def get_payment_history(request):
    #     supplier_id = request.GET.get('supplier_id')
    #     start_date = request.GET.get('start_date')
    #     end_date = request.GET.get('end_date')
    #
    #     invoices = Invoice.objects.filter(supplier_id=supplier_id)
    #     if start_date:
    #         invoices = invoices.filter(date__gte=start_date)
    #     if end_date:
    #         invoices = invoices.filter(date__lte=end_date)
    #
    #     invoices_data = list(invoices.values())
    #
    #     return JsonResponse({'invoices': invoices_data})
    def createsupliers(self, request):
        response = ApiResponse()
        helper = Helpers()
        # Actual student saving// an instance a class

        Suppliers.objects.create(

            businessName=request.data.get('businessName'),
            supplieridNO=request.data.get('supplieridNO'),
            prefix=request.data.get('prefix'),
            firstname=request.data.get('firstname'),
            middlename=request.data.get('middlename'),
            lastname=request.data.get('lastname'),
            phoneNumber=request.data.get('phoneNumber'),
            altPhone=request.data.get('altPhone'),
            email=request.data.get('email'),
            address=request.data.get('address'),
            city=request.data.get('city'),
            postalCode=request.data.get('postalCode'),
            country=request.data.get('country'),
            openingBalance=request.data.get('openingBalance')

        )
        student_instance = suppliers.objects.get(pk=None)
        virtual_account = helper.create_student_account()

    from .models import SuppliersAccount



    def calculate_total_amount(self, request):  # Add request parameter if needed
        supplier_collections = Suppliers.objects.all()

        openingBalance = sum(float(supplier.openingBalance) for supplier in supplier_collections)

        return Response({
            'supplier Collection': openingBalance,

        })

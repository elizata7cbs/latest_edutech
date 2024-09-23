import os
from decimal import Decimal

import django
from django.core.exceptions import ValidationError
from django.db.models import Sum, F
from django.db.models.signals import post_save
from django.dispatch import receiver
from expenses.models import Expenses
from fee.models import StudentFeeCategories, FeeCategoryTransaction
from feecategories.models import FeeCategories, VirtualAccount
# from notifications.models import EmailRecord
from parents.models import Parents

from payfee.models import Payments, RecordTransaction
from django.db import models

# from reconciliation.models import UploadedFile
from schools.models import Schools
from studentsparents.models import StudentsParents
from suppliers.models import Suppliers, SuppliersAccount

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from parents.models import Parents
from payfee.models import RecordTransaction
from studentsparents.models import StudentsParents
from django.db.models import Sum
# Manually configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edutech_payment_engine.settings')
django.setup()
import os
import random
from django.core.mail import send_mail
from rest_framework import status, response
from edutech_payment_engine.settings import BASE_DIR
from authuser.models import OTP
from datetime import timedelta, datetime, date
from django.utils import timezone

from students.models import Students, StudentAccount


#validate the document before uploading
class Helpers:
    def validate_file(self, file):
        ext = os.path.splitext(file.name)[1].lower()
        valid_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx']
        if ext not in valid_extensions:
            return False, "Unsupported file extension."
        return True, None

    #send emails to all parents with balances
    # @receiver(post_save, sender=EmailRecord)
    # def send_email_and_calculate_balances(sender, instance, **kwargs):
    #     subject = instance.subject
    #     message_text = instance.message
    #
    #     parents = Parents.objects.all()
    #     for parent in parents:
    #         studentsparents_records = StudentsParents.objects.filter(parentID=parent)
    #         students_data = []
    #         for record in studentsparents_records:
    #             student = record.studentID
    #
    #             # Calculate the total debit and credit for the specified student
    #             total_debit = RecordTransaction.objects.filter(student_id=student.id).aggregate(Sum('debit'))[
    #                               'debit__sum'] or 0
    #             total_credit = RecordTransaction.objects.filter(student_id=student.id).aggregate(Sum('credit'))[
    #                                'credit__sum'] or 0
    #
    #             # Calculate the total balance
    #             total_balance = total_debit - total_credit
    #
    #             student_data = {
    #                 'firstName': student.firstName,
    #                 'lastName': student.lastName,
    #                 'balance': total_balance,
    #             }
    #             students_data.append(student_data)
    #
    #         # Construct the message content
    #         message_content = f"{message_text}\n\n"
    #         message_content += "Here are the details of your children:\n"
    #         for student in students_data:
    #             message_content += f"{student['firstName']} {student['lastName']}: Balance - {student['balance']}\n"
    #
    #         send_mail(
    #             subject,
    #             message_content,
    #             settings.DEFAULT_FROM_EMAIL,
    #             [parent.email],
    #             fail_silently=False,
    #         )

    def _init_(self):
        self.schools_counter = {}

    def generateSchoolCode(self, name):
        while True:
            splitted_name = name.split(' ')
            initials = ''.join([n[0] for n in splitted_name]).upper()

            if initials not in self.schools_counter:
                self.schools_counter[initials] = 1

            primary_key = str(self.schools_counter[initials]).zfill(3)
            self.schools_counter[initials] += 1

            school_code = f"{initials}-{primary_key}"

            # Check if the generated code already exists in the database
            if not Schools.objects.filter(school_code=school_code).exists():
                return school_code



    def generateSchoolId(self):
        pass

    # def perform_search(self,search_query):
    #     # Implement your search logic here
    #     # For example, you could search a database or external API based on the query
    #     # Return the search results
    #     # This is just a placeholder example
    #     return ['result1', 'result2', 'result3']

    # create school code
    def generateSchoolId(self, school_name, country_code):
        """Generates a unique school code based on name and country code, with validation.

        Args:
            school_name: The name of the school.
            country_code: The country code of the school.

        Returns:
            A unique school code string if successful, None otherwise.
        """

        # Validate school name format (optional, adjust as needed)
        if not school_name or not school_name.isalnum() or len(school_name) > 50:
            return None  # Invalid school name format

        # Validate country code format (alphanumeric, 2-3 characters)
        if not country_code or not country_code.isalnum() or len(country_code) not in [2, 3]:
            return None  # Invalid country code format

        # Generate the base school code
        school_code = self.generate_base_code(school_name, country_code)

        # Check for uniqueness in the database
        while Schools.objects.filter(school_code=school_code).exists():
            # If a duplicate is found, increment the count and regenerate
            count = int(school_code.split('-')[-1])  # Extract the count from the code
            school_code = self.generate_base_code(school_name, country_code, count + 1)

        return school_code

    def generateUniqueId(self, schoolCode, admNumber):
        unique = f'{schoolCode}-{admNumber}'
        return str(unique)

    # generate category code
    def category_code(self, name):
        # Get the first two letters of the category name
        prefix = name[:2].lower()

        # Generate a random three-digit number
        random_numbers = ''.join(random.choices('0123456789', k=3))

        # Combine the prefix and random numbers to create the category code
        categorycode = f"{prefix}{random_numbers}"

        return categorycode

    def create_student_fee_categories(self):
        """
        Function to create new entries in StudentFeeCategories
        based on the associated FeeCategories.
        """
        # Retrieve all FeeCategories objects
        fee_categories = FeeCategories.objects.all()

        # Iterate over each FeeCategories object
        for fee_category in fee_categories:
            # Create a new StudentFeeCategories entry for each FeeCategories
            StudentFeeCategories.objects.create(
                student=fee_category.student,
                fee_category=fee_category,
                amount=fee_category.amount
            )

    def generate_reference(self, paymentmode, payment_date):
        reference = f'{paymentmode}-{payment_date}'
        return reference

    def calculate_balance(self, debit, credit):
        # Calculate the balance before saving
        balance = debit - credit
        return balance

    def generateUniqueexpenseid(self):
        pass

    def generatecategorycode(self, name, description):
        categorycode = f'{name}-{description}'
        return categorycode

    def generateUniquefeepaymentid(self):
        pass

    # Create feecategories accounts
    @receiver(post_save, sender=FeeCategories)
    def create_virtual_account(sender, instance, created, **kwargs):
        if created:
            VirtualAccount.objects.create(category=instance)

    # credit feecategories account when selected
    @receiver(post_save, sender=StudentFeeCategories)
    def credit_fee_categories_virtual_account(sender, instance, created, **kwargs):
        if created:
            fee_category = instance.fee_category
            virtual_account, _ = VirtualAccount.objects.get_or_create(category=fee_category)
            virtual_account.credit += fee_category.amount
            virtual_account.save()

    # creating student virtual account
    @receiver(post_save, sender=Students)
    def create_student_account(sender, instance, created, **kwargs):
        if created:
            # Create a student account when a new student is created
            StudentAccount.objects.create(student=instance)

    #  debit  student account when feecategories is selected
    @receiver(post_save, sender=StudentFeeCategories)
    def debit_student_account(sender, instance, created, **kwargs):
        if created:
            student = instance.student
            student_account, _ = StudentAccount.objects.get_or_create(student=student)
            student_account.debit += instance.fee_category.amount
            student_account.save()

    # #debit all student account  if selected ALL and credit fee virtual account
    @receiver(post_save, sender=FeeCategories)
    def debit_all_students_and_credit_fee_category(sender, instance, created, **kwargs):
        if created and instance.apply == 'ALL':
            # Debit all student accounts
            total_debit = 0
            for student_account in StudentAccount.objects.all():
                student_account.debit += instance.amount
                student_account.save()
                total_debit += instance.amount

            # Credit the fee category's virtual account with the total debit amount
            fee_category_account, _ = VirtualAccount.objects.get_or_create(category=instance)
            fee_category_account.credit += total_debit
            fee_category_account.balance += total_debit
            fee_category_account.save()

    # credit student account when payment is made
    @receiver(post_save, sender=Payments)
    def credit_student_account(sender, instance, created, **kwargs):
        if created:
            # Convert instance.amount_paid to Decimal
            amount_paid_decimal = Decimal(instance.amount_paid)

            # Fetch the student account associated with the student
            student_account = StudentAccount.objects.get(student=instance.student)

            # Update the credit balance of the student account
            student_account.credit += amount_paid_decimal
            student_account.save()

    # record debit transaction when fee is selected

    @receiver(post_save, sender=StudentFeeCategories)
    def record_fee_category_amount(sender, instance, created, **kwargs):
        """
        Records the fee category amount when a new StudentFeeCategories object is created.
        """
        if created:
            fee_category = instance.fee_category

            # Create a new transaction for the fee category
            RecordTransaction.objects.create(
                student=instance.student,
                description=f"Category Selected for {fee_category.name}",
                debit=fee_category.amount,
                credit=0,
                balance=None  # You may need to calculate this based on other transactions
            )

    # debits the student with current term upon creation
    @receiver(post_save, sender=Students)
    def create_student_fee_categories(sender, instance, created, **kwargs):
        """
        Automatically assigns all fee categories for term one to the student as debit transactions.
        """
        if created:
            term_one_fee_categories = FeeCategories.objects.filter(term="Term1")

            for fee_category in term_one_fee_categories:
                StudentFeeCategories.objects.create(
                    student=instance,
                    fee_category=fee_category
                )

                # Record debit transaction for the fee category
                RecordTransaction.objects.create(
                    student=instance,
                    description=f"Category Selected for {fee_category.name}",
                    debit=fee_category.amount,
                    credit=0,
                    balance=None  # You may need to calculate this based on other transactions
                )

    # record credit  transaction when payment is made
    @receiver(post_save, sender=Payments)
    def record_credit_transaction(sender, instance, created, **kwargs):
        if created:
            # Create a new transaction for fee payment
            RecordTransaction.objects.create(
                student=instance.student,
                description=f"Fee payment made: {instance.reference}",
                debit=0,
                credit=instance.amount_paid,
                balance=None  # You may need to calculate this based on other transactions
            )

        # creating supplier account
        @receiver(post_save, sender=Suppliers)
        def create_supplier_account(sender, instance, created, **kwargs):
            if created:
                # Create a student account when a new student is created
                SuppliersAccount.objects.create(supplier=instance)

        # crediting supplier account
        # @receiver(post_save, sender=SuppliersPayment)
        # def credit_supplier_account(sender, instance, created, **kwargs):
        #     if created:
        #         # Convert instance.amount_paid to Decimal
        #         amount_paid_decimal = Decimal(instance.amount_paid)
        #
        #         # Fetch the supplier account associated with the student
        #         supplier_account = SuppliersAccount.objects.get(supplier=instance.supplier)
        #
        #         # Update the credit balance of the student account
        #         supplier_account.credit += amount_paid_decimal
        #         supplier_account.save()

        # debit supplier account
        @receiver(post_save, sender=Suppliers)
        def debit_supplier_account(sender, instance, created, **kwargs):
            if created:
                # Convert instance.openingBalance to Decimal
                openingBalance = Decimal(instance.openingBalance)
                supplier_account, _ = SuppliersAccount.objects.get_or_create(supplier=instance)
                supplier_account.debit += openingBalance
                supplier_account.save()

        # create an expense account

        def create_expense_account():
            """
            Create the 'Expense Account' if it doesn't exist.
            """
            if not Account.objects.filter(name='Expense Account').exists():
                Account.objects.create(name='Expense Account', balance=0)

            def save_payment_data(self, payment_data, receipt_number):
                from feecollections.models import FeeCollections
                fee_payment = FeeCollections.objects.create(
                    receipt_number=receipt_number,
                    amount=payment_data['amountPaid'],
                    date=timezone.now(),
                )
                return fee_payment

            # def generate_receipt_number(sender, instance, **kwargs):
            #     from feecollections.models import FeeCollections
            #     if not instance.receipt_number:
            #         school_code = instance.school.school_code
            #         receipts_count = FeeCollections.objects.filter(school=instance.school).count()
            #
            #         # Determine the starting point for receipt numbers
            #         starting_number = receipts_count + 1
            #
            #         # Generate receipt number
            #         if starting_number <= 10:
            #             instance.receipt_number = f"{school_code}-FEE-{starting_number:02d}"
            #         else:
            #             last_receipt = FeeCollections.objects.filter(school=instance.school).order_by('-id').first()
            #             last_receipt_number = last_receipt.receipt_number.split('-')[2]
            #             last_receipt_number = int(last_receipt_number) + 1
            #             while True:
            #                 receipt_number = f"{school_code}-FEE-{last_receipt_number:02d}"
            #                 if not FeeCollections.objects.filter(receipt_number=receipt_number).exists():
            #                     instance.receipt_number = receipt_number
            #                     break
            #                 last_receipt_number += 1

        # def generate_receipt_and_save_payment(school_code, payment_data):
        #     from feecollections.models import FeeCollections
        #
        #     try:
        #         school = Schools.objects.get(school_code=school_code)
        #     except Schools.DoesNotExist:
        #         return None, None
        #
        #     # Generate a UUID for the incremental value
        #     incremental_value = str(uuid.uuid4())
        #
        #     # Construct the receipt number
        #     receipt_number = f"{school_code.upper()}-FEE-{incremental_value}"
        #
        #     # Check if the receipt number already exists
        #     while FeeCollections.objects.filter(receipt_number=receipt_number).exists():
        #         # If it exists, generate a new UUID and construct a new receipt number
        #         incremental_value = str(uuid.uuid4())
        #         receipt_number = f"{school_code.upper()}-FEE-{incremental_value}"
        #
        #     # Save the payment data with the generated receipt number
        #     fee_payment = FeeCollections.save_payment_data(payment_data, receipt_number)
        #
        #     return receipt_number, fee_payment

        def calculate_next_due_date(start_date, payment_date, frequency):
            if frequency == 'daily':
                frequency_days = 1
            elif frequency == 'weekly':
                frequency_days = 7
            elif frequency == 'bi_weekly':
                frequency_days = 14
            elif frequency == 'monthly':
                frequency_days = 30  # Assuming 30 days in a month

            # Calculate the number of days since the start date
            days_since_start = (payment_date - start_date).days

            # Calculate the number of periods completed
            periods_completed = days_since_start // frequency_days

            # Calculate the next due date based on the number of completed periods
            next_due_date = start_date + timedelta(days=(periods_completed + 1) * frequency_days)

            return next_due_date

    def otp(self, name, otp, email):
        # verification_link = f"https://3c97-2c0f-fe38-2102-f942-62c5-78b8-6e43-79e6.ngrok-free.app/spinner/account
        # /verify/{email}"
        try:
            email_content = f"""
            <html>
                <head>
                    <style>
                        font-size: 12px;
                    </style>
                </head>
                <body>
                    <p>Hello {name},</p>
                    <p style="font-size: 20px, color: black;">Use: <span class="otp" >{otp}</span></p>
                    <p>If you did not request this, please ignore. Do not share OTP with anyone.</p>
                </body>
            </html>
            """
            sent = send_mail(
                'Verification OTP',
                '',
                'no-reply@gmail.com',
                [email],
                fail_silently=False,
                html_message=email_content,
            )
            return sent

        except Exception as e:
            # response.setMessage(f"Error sending email: {str(e)}")
            sent = 0
            print(f"Error sending email: {str(e)}")
        return sent

    def generateotp(self):
        characters = "0123456789"
        otp = ''.join(random.choice(characters) for _ in range(6))
        return otp

    def saveotp(self, otp, email):
        expiry_time = timezone.now() + timedelta(minutes=5)
        otpData = OTP(
            otp=otp,
            email=email,
            expirydate=expiry_time
        )
        otpData.save()
        return None

    def send_generated_password(self, name, username, password, email):
        try:
            email_content = f"""
            <html>
                <head>
                    <style>
                        font-size: 12px;
                    </style>
                </head>
                <body>
                    <p>Hello {name},</p>
                    <p>Welcome to Elimu Pay School Payment Management System! We are delighted to have you join our community of financial administrators and students.</p>
                    <p>Your account has been created successfully!</p>
                    <p>Please use the below as your username and password.</p>

                    <p>Your username: {username}</p>
                    <p>Your new password: {password}</p>

                </body>
            </html>
            """
            sent = send_mail(
                'Your New Account Credentials',
                '',
                'no-reply@gmail.com',
                [email],
                fail_silently=False,
                html_message=email_content,
            )
            return sent

        except Exception as e:
            sent = 0
            print(f"Error sending email: {str(e)}")
        return sent

    def log(self, request):
        current_date = datetime.now().strftime('%Y.%m.%d')
        log_file_name = f"{current_date}-request.log"
        log_dir = os.path.join(BASE_DIR, 'utils/logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file_path = os.path.join(log_dir, log_file_name)
        log_string = f"[{datetime.now().strftime('%Y.%m.%d %I.%M.%S %p')}] => method: {request.method} uri: {request.path} queryString: {request.GET.urlencode()} protocol: {request.scheme} remoteAddr: {request.META.get('REMOTE_ADDR')} remotePort: {request.META.get('REMOTE_PORT')} userAgent: {request.META.get('HTTP_USER_AGENT')}"
        if os.path.exists(log_file_path):
            mode = 'a'
        else:
            mode = 'w'
        with open(log_file_path, mode) as log_file:
            log_file.write(log_string + '\n')

        # create an expense account

        def create_expense_account(self):
            """
            Create the 'Expense Account' if it doesn't exist.
            """
            if not Account.objects.filter(name='Expense Account').exists():
                Account.objects.create(name='Expense Account', balance=0)

        def debit_expense_account(expense):
            """
            Debits the expense account associated with the given expense.

            Args:
                expense (Expenses): The expense object for which to debit the account.

            Raises:
                Account.DoesNotExist: If the "Expense Account" is not found.
            """

            try:
                # Retrieve the 'Expense Account' object
                expense_account = Account.objects.get(name='Expense Account')
            except Account.DoesNotExist:
                print("Expense Account does not exist")
                return

            # Update the balance of the expense account by subtracting the expense amount
            expense_account.balance = F('balance') - expense.amount
            expense_account.save()

        def calculate_total_expenses(filters=None):
            """
            Calculates the total expense amount based on optional filters.

            Args:
                filters (dict, optional): A dictionary containing filters for expenses.

            Returns:
                float: The total expense amount.
            """

            expenses = Expenses.objects.all()
            if filters:
                expenses = expenses.filter(**filters)
            return expenses.aggregate(total=Sum('amount'))['total'] or 0

        def calculate_expense_breakdown_by_project(self):
            """
            Calculates the expense breakdown for a specific project.

            Args:
                self (int): The ID of the project.

            Returns:
                dict: A dictionary containing project expense details.
            """

            expenses = Expenses.objects.filter(project=self)
            return {
                'total_expense': expenses.aggregate(total=Sum('amount'))['total'] or 0,
                # You can add further breakdowns like expense types or categories here
            }

    # record credit when fee is selected
    @receiver(post_save, sender=StudentFeeCategories)
    def create_or_update_fee_category_transaction(sender, instance, created, **kwargs):
        fee_category = instance.fee_category
        student = instance.student

        if created:
            FeeCategoryTransaction.objects.create(
                student=student,
                feecategory=fee_category,
                description=f"Category selected: {fee_category.name}",
                debit=0,
                credit=fee_category.amount,
                balance=fee_category.amount,
                transaction_date=date.today()
            )
        else:
            transaction = FeeCategoryTransaction.objects.filter(
                student=student,
                feecategory=fee_category
            ).first()

            if transaction:
                transaction.credit = fee_category.amount
                transaction.balance = transaction.debit - transaction.credit
                transaction.save()

    # record a debit when payment is done
    @receiver(post_save, sender=Payments)
    def apply_payment(sender, instance, **kwargs):
        student = instance.student
        payment_amount = instance.amount_paid  # Assuming 'amount' holds the payment amount

        priority_order = ['Catering', 'transport', 'tuition']

        transactions = StudentFeeCategories.objects.filter(student=student).order_by(
            models.Case(
                models.When(fee_category__name='Catering', then=1),
                models.When(fee_category__name='transport', then=2),
                models.When(fee_category__name='tuition', then=3),
                default=4
            )
        )

        for student_fee_category in transactions:
            if payment_amount <= 0:
                break

            transaction = FeeCategoryTransaction.objects.filter(
                student=student,
                feecategory=student_fee_category.fee_category
            ).first()

            if not transaction:
                transaction = FeeCategoryTransaction.objects.create(
                    student=student,
                    feecategory=student_fee_category.fee_category,
                    debit=0,
                    credit=0,
                    balance=0
                )

            amount_needed = transaction.feecategory.amount - transaction.debit
            if amount_needed > 0:
                amount_to_apply = min(amount_needed, payment_amount)
                transaction.debit += amount_to_apply
                transaction.save()

                FeeCategoryTransaction.objects.create(
                    student=student,
                    feecategory=student_fee_category.fee_category,
                    description=f"Payment applied to {transaction.feecategory.name}",
                    debit=amount_to_apply,
                    credit=0,
                    balance=transaction.credit - transaction.debit,
                    transaction_date=timezone.now().date()
                )

                payment_amount -= amount_to_apply

        if payment_amount > 0:
            # Handle remaining amount if necessary
            FeeCategoryTransaction.objects.create(
                student=student,
                feecategory=None,  # Assuming no specific category for remaining amount
                description="Remaining payment amount",
                debit=payment_amount,
                credit=0,
                balance=-payment_amount,
                transaction_date=timezone.now().date()
            )
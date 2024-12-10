from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json
import datetime
from .models import Service, Customer, Worker
from django.shortcuts import render

from django.db import connection
from django.http import JsonResponse

def execute_sql_query(query, params=None):
    """Helper function to execute raw SQL queries."""
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        if cursor.description:  # Check if the query returns data
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
        return None

@login_required(login_url="/landingpage")
def show_main(request):
    context = {
        "title": "Welcome to Sijarta",
        "last_login": request.COOKIES["last_login"],
    }
    return render(request, "home.html", context)

def register(request):
    context = {"title": "Registration Page"}
    return render(request, "register.html", context)

def register_customer(request):
    if request.method == 'POST':
        # temporary while there is no register user data
        name = 'Dave'
        sex = 'M'
        phone_number = '1234567890'
        password = make_password('Dave1234')
        birthdate = '2000-09-10'
        address = 'Street 1, LA'
        '''
        name = request.POST['name']
        sex = request.POST['sex']
        phone_number = request.POST['phone_number']
        password = make_password(request.POST['password'])
        birthdate = request.POST['birthdate']
        address = request.POST['address']
        '''
        Customer.objects.create(
            name = name,
            sex = sex,
            phone_number = phone_number,
            password = password,
            birthdate = birthdate,
            address = address
        )

        # For debugging
        messages.success(request, "Customer registration successful!")
        return redirect('login_user')

    # TODO: Check if the render is fine for customer
    return render(request, 'register_customer.html')

    # Previous code
    # 
    # if request.method == "POST":
    #     form = CustomerRegistrationForm(request.POST)
    #     if form.is_valid():
    #         # Save user as a Customer
    #         user = form.save(commit=False)
    #         user.user_type = 'customer'
    #         user.save()
    #         messages.success(request, "Your account as a Customer has been successfully created!")
    #         return redirect("main:login")
    # else:
    #     form = CustomerRegistrationForm()
    
    # context = {"form": form}
    # return render(request, "register_customer.html", context)


def register_worker(request):
    if request.method == 'POST':
        name = request.POST['name']
        sex = request.POST['sex']
        phone_number = request.POST['phone_number']
        password = make_password(request.POST['password'])
        birthdate = request.POST['birthdate']
        address = request.POST['address']

        # Additional parameters to be filled for worker
        bank_name = request.POST['bank_name']
        account_number = request.POST['account_number']
        npwp = request.POST['npwp']
        avatar_url = request.POST['avatar_url']

        Worker.objects.create(
            name = name,
            sex = sex,
            phone_number = phone_number,
            password = password,
            birthdate = birthdate,
            address = address,
            bank_name = bank_name,
            account_number = account_number,
            npwp = npwp,
            avatar_url = avatar_url
        )

        # For debugging
        messages.success(request, "Worker registration successful!")
        return redirect('login_user')

    # TODO: Check if the render is fine for customer
    return render(request, 'register_worker.html')

    # Previous code
    # 
    # if request.method == "POST":
    #     form = WorkerRegistrationForm(request.POST)
    #     if form.is_valid():
    #         # Save user as a Worker
    #         user = form.save(commit=False)
    #         user.user_type = 'worker'
    #         user.save()
    #         messages.success(request, "Your account as a Worker has been successfully created!")
    #         return redirect("main:login")
    # else:
    #     form = WorkerRegistrationForm()

    # context = {"form": form}
    # return render(request, "register_worker.html", context)

def login_user(request):
    if request.method == "POST":
        
        phone_number = request.POST['phone_number']
        checked_password = check_password(request.POST['password'])
        user = authenticate(request, phone_number=phone_number, password=checked_password)

        if user is not None:
            login(request, user)
            response = HttpResponseRedirect(reverse("main:show_main"))  
            response.set_cookie("last_login", str(datetime.datetime.now())) 
            return response
        else:
            messages.error(request, "Invalid phone number or password.")

    return render(request, "login.html")

    # Old Code
    # else:
        # For now, pass
        # pass
        # What should I change for this?
        # Update: actually, let it go
        # form = AuthenticationForm()

    # context = {"form": form}
    # return render(request, "login.html", context)


def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse("main:landingpage"))
    response.delete_cookie("last_login")
    return response


def home(request):
    user = request.user
     
    category_subcategory = """
        SELECT 
            sc.SCId AS CategoryId,
            sc.Name AS CategoryName,
            ssc.SSCId AS SubcategoryId,
            ssc.Name AS SubcategoryName,
            ssc.Description AS SubcategoryDescription
        FROM 
            service_category sc
        JOIN 
            service_subcategory ssc
        ON 
            sc.SCId = ssc.SCId
        ORDER BY 
            sc.Name, ssc.Name;
    """
    params = [user]
    category_subcategory_result = execute_sql_query(category_subcategory, params)

    context = {
        "title": "Sijarta Homepage",
        "user": user,
        "category_subcategory_list": category_subcategory_result,
    }

    print(category_subcategory_result)

    return render(request, "home.html", context)


def subcategory(request):
    # TODO: Continue this later
    # user = request.user
    # if hasattr(user, 'customer'):
    #     customer = user.customer
    # elif hasattr(user, 'worker'):
    #     worker = user.worker

    
    context = {"title": "Sijarta Subcategory"}
    return render(request, "subcategory.html", context)


@login_required(login_url="/landingpage")
def customer_profile(request):
    context = {"title": "My Profile"}
    return render(request, "customer_profile.html", context)

@login_required(login_url="/landingpage")
def worker_profile(request):
    context = {"title": "My Profile"}
    return render(request, "worker_profile.html", context)

# @login_required(login_url="/landingpage") # TODO uncomment
def mypay(request):
    # user_id = 'USR00' # TODO should be based on request
    # Proposed solution:
    #user_id = request.user
    user_id = 'USR00'
    print(user_id)
     
    user_query = """
        SELECT "PhoneNum", "MyPayBalance", "Username", "UserId"
        FROM "user"
        WHERE "UserId" = %s
    """
    params = [user_id]
    user_result = execute_sql_query(user_query, params)

    transactions_query = """
        SELECT t."Nominal", t."Date", t."MyPayId", c."Name"
        FROM tr_mypay t
        JOIN tr_mypay_category c ON t."CategoryId" = c."MyPayCatId"
        WHERE t."UserId" = %s
        ORDER BY t."Date" DESC 
    """
    params = [user_id]
    transactions_result = execute_sql_query(transactions_query, params)

    context = {
        "user": request.user,
        "user_info": user_result[0],
        "transactions": transactions_result,
    }

    print(user_result)
    print(transactions_result)

    return render(request, "mypay.html", context)


# @login_required(login_url="/landingpage") # TODO uncomment
def mypay_transaction(request):
    
    user_id = 'USR00' # TODO should be based on request
    account = None
     
    # try to query userid in customer
    customer_query = """
        SELECT *
        FROM customer
        WHERE "CustomerId" = %s
    """
    customer_result = execute_sql_query(customer_query, [user_id])
    if len(customer_result) > 0:
        account = 'customer'
    
    # else try to query userid in worker
    else:
        worker_query = """
            SELECT *
            FROM worker
            WHERE "WorkerId" = %s
        """
        worker_result = execute_sql_query(worker_query, [user_id])
        if len(customer_result) > 0:
            account = 'worker'

    # if doesn't exist, then user neither customer nor worker
    
    # organize the service categories
    categories = []
    services = []
    if account == 'customer':
        categories = [
            ('Top Up'),
            ('Service Payment'),
            ('Transfer'),
            ('Withdrawal'),
        ]

        # query service orders that have not yet been paid
        services = []

        service_query = """
                    SELECT o."Id", ssc."Name", o."Session", o."TotalPrice"
                    FROM tr_service_order o
                    JOIN tr_order_status ts ON o."Id" = ts."ServiceTrId"
                    JOIN order_status s ON ts."StatusId" = s."StatusId"
                    JOIN service_subcategory ssc ON o."ServiceCategoryId" = ssc."SSCId"
                    WHERE o."CustomerId" = %s
                    AND s."Status" = %s
                    """
        services = execute_sql_query(service_query, [user_id, "Waiting for Payment"])
        print(services)

    elif account == 'worker':
        categories = [
            ('Top Up'),
            ('Transfer'),
            ('Withdrawal'),
        ]
    
    context = {
        'states': categories,
        'services': services
    }

    if request.method == 'POST':
        print("POST request triggered")

        state = request.POST.get('state')
        user_id = 'USR00' # should be based on request

        try:
            # Handle each state
            if state == 'Top Up':
                print("MyPay Top Up")
                amount = float(request.POST.get('top_up_amount'))
                if amount <= 0:
                    raise ValueError("Top-up amount must be positive.")
                
                # increase user's MyPay balance
                query = """
                    UPDATE "user"
                    SET "MyPayBalance" = "MyPayBalance" + %s
                    WHERE "UserId" = %s
                """
                #execute_sql_query(query, [amount, user_id])

                # Add transaction to tr_mypay
                query = """
                    INSERT INTO tr_mypay (UserId, Date, Nominal, CategoryId)
                    VALUES (%s, CURRENT_DATE, %s, %s)
                """
                params = [user_id, amount, "MPC00"]
                #execute_sql_query(query, params)

            elif state == 'Service Payment':
                service_id = request.POST.get('service_id')
                amount_due = float(request.POST.get('service_price'))
                print("MyPay Service Payment id: ", service_id)

                service_query = """
                    SELECT o."Id", o."TotalPrice", p."Name"
                    FROM tr_service_order o
                    JOIN payment_method p ON o."PaymentMethodId" = p."PaymentMethodId"
                    WHERE o."Id" = %s
                    """
                services = execute_sql_query(service_query, [service_id])

                if len(services) == 0:
                    raise ValueError("Cannot pay for this service.")
                
                amount_due = services[0]["TotalPrice"]
                payment_method = services[0]["Name"]
                
                # if payment method is mypay, deduct from MyPay
                if payment_method == "MyPay":
                    # Check if sender has enough funds
                    balance_query = """
                        SELECT "MyPayBalance" 
                        FROM "user"
                        WHERE "UserId" = %s
                        """
                    balance = execute_sql_query(balance_query, [user_id])
                    if balance < amount_due:
                        raise ValueError("Insufficient MyPay balance.")

                    # withdraw amount from user for service
                    query = """
                        UPDATE "user"
                        SET "MyPayBalance" = "MyPayBalance" - %s
                        WHERE "UserId" = %s
                    """
                    #execute_sql_query(query, [amount_due, user_id])

                    # Add transaction to tr_mypay
                    query = """
                        INSERT INTO tr_mypay (UserId, Date, Nominal, CategoryId)
                        VALUES (%s, CURRENT_DATE, %s, %s)
                    """
                    params = [user_id, -amount_due, "MPC01"]
                    #execute_sql_query(query, params)

                # set service status as looking for worker
                update_query = """
                    UPDATE tr_order_status 
                    SET "StatusId" = %s
                    WHERE "ServiceTrId" = %s
                    """
                params = ['STI03', service_id]
                result = execute_sql_query(update_query, params)


            elif state == 'Transfer':
                print("MyPay Transfer")
                recipient_phone = request.POST.get('recipient_phone')
                amount = float(request.POST.get('transfer_amount'))
                if amount <= 0:
                    raise ValueError("Transfer amount must be positive.")
                
                # Try to get user id of recipient phone
                # Check if phone number to transfer to exists
                phone_query = """
                    SELECT * 
                    FROM "user"
                    WHERE "PhoneNum" = %s
                    """
                recipient = execute_sql_query(phone_query, [recipient_phone])
                if len(recipient) == 0:
                    raise ValueError("Cannot transfer to that account.")
                recipient_id = recipient[0]["UserId"]
                print(recipient_id)
                if recipient_id == user_id:
                    raise ValueError("Cannot transfer to self.")

                # Check if sender has enough funds
                balance_query = """
                    SELECT "MyPayBalance" 
                    FROM "user"
                    WHERE "UserId" = %s
                    """
                balance = execute_sql_query(balance_query, [user_id])
                if balance < amount:
                    raise ValueError("Insufficient balance.")

                # Deduct from sender
                deduct_query = """
                    UPDATE "user"
                    SET "MyPayBalance" = "MyPayBalance" - %s
                    WHERE "UserId" = %s
                """
                #execute_sql_query(deduct_query, [amount, user_id])

                # Add transaction to tr_mypay of sender
                query = """
                    INSERT INTO tr_mypay (UserId, Date, Nominal, CategoryId)
                    VALUES (%s, CURRENT_DATE, %s, %s)
                """
                params = [user_id, -amount, "MPC02"]
                #execute_sql_query(query, params)

                # Add to recipient
                add_query = """
                    UPDATE "user"
                    SET "MyPayBalance" = "MyPayBalance" + %s
                    WHERE "PhoneNum" = %s
                """
                #execute_sql_query(add_query, [amount, recipient_phone])

                # Add transaction to tr_mypay of recipient
                query = """
                    INSERT INTO tr_mypay (UserId, Date, Nominal, CategoryId)
                    VALUES (%s, CURRENT_DATE, %s, %s)
                """
                params = [recipient_id, amount, "MPC00"]
                #execute_sql_query(query, params)

            elif state == 'Withdrawal':
                print("MyPay Withdrawal")
                bank_name = request.POST.get('bank_name')
                account_number = request.POST.get('bank_account')
                withdrawal_amount = float(request.POST.get('withdrawal_amount'))
                if withdrawal_amount <= 0:
                    raise ValueError("Withdrawal amount must be positive.")
                
                # Check if sender has enough funds
                balance_query = """
                    SELECT "MyPayBalance" 
                    FROM "user"
                    WHERE "UserId" = %s
                    """
                balance = execute_sql_query(balance_query, [user_id])
                if balance < amount:
                    raise ValueError("Insufficient balance.")
                
                deduct_query = """
                    UPDATE "user"
                    SET "MyPayBalance" = "MyPayBalance" - %s
                    WHERE "UserId" = %s
                """
                #execute_sql_query(deduct_query, [amount, user_id])

                # Add transaction to tr_mypay
                query = """
                    INSERT INTO tr_mypay (UserId, Date, Nominal, CategoryId)
                    VALUES (%s, CURRENT_DATE, %s, %s)
                """
                params = [user_id, -amount, "MPC04"]
                #execute_sql_query(query, params)

            messages.success(request, "Transaction successful!")

        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, 'mypaytransaction.html', context)


#@login_required(login_url="/landingpage") # TODO uncomment
def service_job(request):
    user_id = 'USR02'
    # fetch which categories worker is registered for
    categories_query = """
        SELECT w."SCId" AS "CategoryId", s."Name"
        FROM worker_service_category w
        JOIN service_category s ON w."SCId" = s."SCId"
        WHERE "WorkerId" = %s
        """
    categories = execute_sql_query(categories_query, [user_id])
    print(categories)

    # fetch which subcategories worker is registered for
    subcategories_query = """
        SELECT ss."SSCId", ss."Name", ss."SCId"
        FROM service_subcategory ss
        JOIN worker_service_category wsc ON ss."SCId" = wsc."SCId"
        WHERE wsc."WorkerId" = %s
        """
    subcategories = execute_sql_query(subcategories_query, [user_id])
    print(subcategories)

    services = []
    
    # Filter services if search form is submitted
    if request.method == 'POST' and 'search' in request.POST:
        print("search activated")
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory')

        if subcategory_id:
            services_query = """
                SELECT tso."Id" as "OrderId", tso."TotalPrice", tso."OrderDate", tso."Session", u."Username", ss."Name" AS "ServiceName"
                FROM tr_service_order tso
                JOIN tr_order_status tos ON tso."Id" = tos."ServiceTrId"
                JOIN "user" u ON tso."CustomerId" = u."UserId"
                JOIN service_subcategory ss ON tso."ServiceCategoryId" = ss."SSCId"
                WHERE tso."ServiceCategoryId" = %s AND tos."StatusId" = %s
            """
            params = [subcategory_id, 'STI03']
            services = execute_sql_query(services_query, params)

        elif category_id:

            services_query = """
                SELECT tso."Id" as "OrderId", tso."TotalPrice", tso."OrderDate", tso."Session", u."Username", ss."Name" AS "ServiceName"
                FROM tr_service_order tso
                JOIN tr_order_status tos ON tso."Id" = tos."ServiceTrId"
                JOIN "user" u ON tso."CustomerId" = u."UserId"
                JOIN service_subcategory ss ON tso."ServiceCategoryId" = ss."SSCId"
                WHERE ss."SCId" = %s AND tos."StatusId" = %s
                """
            params = [category_id, 'STI03']
            services = execute_sql_query(services_query, params)

        else:
            # fetch all services available for worker to take
            services_query = """
                SELECT DISTINCT tso."Id", tso."TotalPrice", tso."OrderDate", tso."Session", u."Username", ss."Name" AS "ServiceName"
                FROM tr_service_order tso
                JOIN tr_order_status tos ON tso."Id" = tos."ServiceTrId"
                JOIN "user" u ON tso."CustomerId" = u."UserId"
                JOIN service_subcategory ss ON tso."ServiceCategoryId" = ss."SSCId"
                JOIN worker_service_category wsc ON ss."SCId" = wsc."SCId"
                WHERE wsc."WorkerId" = %s AND tos."StatusId" = %s
            """
            params = [user_id, 'STI03']
            services = execute_sql_query(services_query, params)
            

        print(services)

    # Handle Accept Order action
    if request.method == 'POST' and 'accept_order' in request.POST:
        order_id = request.POST['order_id']

        # validate that order still exists as looking for workers
        order_query = """
                    SELECT o."Id", o."Session"
                    FROM tr_service_order o
                    JOIN tr_order_status tos ON o."Id" = tos."ServiceTrId"
                    WHERE o."Id" = %s AND tos."StatusId" = %s
                    """
        params = [order_id, 'STI03']
        order = execute_sql_query(order_query, params)

        if len(order) == 0:
            raise ValueError("Cannot accept this service.")
        session = order[0]["Session"]

        # change the status to waiting for worker
        update_query = """
                    UPDATE tr_order_status 
                    SET "StatusId" = %s
                    WHERE "ServiceTrId" = %s
                    """
        params = ['STI04', order_id] 
        execute_sql_query(update_query, params)

        # update the service_order with updated info
        accept_order_query = """
            UPDATE tr_service_order 
            SET "ServiceDate" = CURRENT_DATE, 
            "ServiceTime" = CURRENT_TIMESTAMP + INTERVAL '%s days',
            "WorkerId" = %s
            WHERE "Id" = %s;
        """
        params = [session, user_id, order_id]
        execute_sql_query(accept_order_query, params)

    context = {
        'categories': categories,
        'subcategories': subcategories,
        'services': services,
    }
    return render(request, "servicejob.html", context)


def service_job_status(request):
    statuses = [
        'Waiting For Worker to Depart',
        'Arrived At Location',
        'Providing Service',
        'Service Completed',
        'Order Cancelled'
    ]

    services = [
        {'subcategory_name': 'hello',
         'user_name': 'username',
         'order_date': '2021-12-23',
         'working_date': '2021-12-26',
         'session': 'idk',
         'total_amount': 'money',
         'status': 'Arrived At Location'
    }
    ]

    context = {
        "user": request.user,
        'statuses': statuses,
        'services': services
    }

    return render(request, "servicejobstatus.html", context)


def service_booking(request):
    context = {"title": "Sijarta Service Booking"}
    return render(request, "service_booking.html", context)


def create_testimonial(request):
    return render(request, "create_testimonial.html")


def discount(request):
    return render(request, "discount.html")

def myorder(request):
    return render(request, "myorder.html")

@csrf_exempt
def update_service_status(request, service_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_status = data.get('status')

        try:
            # Update the service object in the database
            service = Service.objects.get(id=service_id)
            service.status = new_status
            service.save()
            return JsonResponse({'success': True})
        except Service.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Service not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def landingpage(request):
    return render(request, "landingpage.html")

def update_customer_profile(request):
    return render(request, "update_customer_profile.html")

def update_worker_profile(request):
    return render(request, "update_worker_profile.html")

@login_required(login_url="/landingpage")
def update_customer_profile(request):
    customer = request.user

    form = CustomerRegistrationForm(request.POST or None, instance=customer)

    if form.is_valid() and request.method == "POST":
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return HttpResponseRedirect(reverse('main:customer-profile'))
    else:
        form = CustomerRegistrationForm(instance=customer)

    context = {"form": form}
    return render(request, "update_customer_profile.html", context)

@login_required(login_url="/landingpage")
def update_worker_profile(request):
    worker = request.user
    if request.method == "POST":
        form = WorkerRegistrationForm(request.POST, instance=worker)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("main:worker-profile")
    else:
        form = WorkerRegistrationForm(instance=worker)

    context = {"form": form}
    return render(request, "update_worker_profile.html", context)

def worker_profile_summary(request):
    return render(request, "worker_profile_summary.html")
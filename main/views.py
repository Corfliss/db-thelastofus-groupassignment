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
# from .models import Service, Customer, Worker
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
        # Customer.objects.create(
        #     name = name,
        #     sex = sex,
        #     phone_number = phone_number,
        #     password = password,
        #     birthdate = birthdate,
        #     address = address
        # )

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

        # Worker.objects.create(
        #     name = name,
        #     sex = sex,
        #     phone_number = phone_number,
        #     password = password,
        #     birthdate = birthdate,
        #     address = address,
        #     bank_name = bank_name,
        #     account_number = account_number,
        #     npwp = npwp,
        #     avatar_url = avatar_url
        # )

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
            sc."SCId" AS CategoryId,
            sc."Name" AS CategoryName,
            ssc."SSCId" AS SubcategoryId,
            ssc."Name" AS SubcategoryName,
            ssc."Description" AS SubcategoryDescription
        FROM 
            service_category sc
        JOIN 
            service_subcategory ssc
        ON 
            sc."SCId" = ssc."SCId"
        ORDER BY 
            sc."Name", ssc."Name";
    """
    
    category_subcategory_result = execute_sql_query(category_subcategory, [])

    # Organize data into a nested dictionary for easy rendering
    category_subcategory_dict = {}

    for row in category_subcategory_result:
        category_id = row['categoryid']
        if category_id not in category_subcategory_dict:
            category_subcategory_dict[category_id] = {
                "name": row['categoryname'],
                "subcategories": []
            }
        
        category_subcategory_dict[category_id]["subcategories"].append({
            "name": row['subcategoryname'],
            "description": row['subcategorydescription']
        })

    context = {
        "title": "Sijarta Homepage",
        "user": user,
        "categories": category_subcategory_dict
    }

    # For debugging purpose
    # print(category_subcategory_result)

    return render(request, "home.html", context)

# @login_required(login_url="/landingpage")
def subcategory(request):
    # This might break the code, if anyone know better, glad to see the fix
    subcategory_name = request.GET.get('subcategory_id')

    params = [subcategory_name]
    query = """
        SELECT "Name", "Description"
        FROM "service_subcategory"
        WHERE Name = %s  
        """
    name_and_description = execute_sql_query(query, params)

    worker_list_query = """
        SELECT U.username
        FROM "auth_user" U
        JOIN "worker" W ON W.user_id = U.id
        JOIN "worker_service_category" WSC ON WSC.worker_id = W.id
        JOIN "service_subcategory" SSC ON SSC.SCId = WSC.service_category_id
        WHERE SSC."Name" = %s;
        """
    worker_list = execute_sql_query(worker_list_query, params)

    testimonial_list_query = """
        SELECT t."Date", t."Text", t."Rating", u."Username"
        FROM "testimony" t
        JOIN "tr_service_order" tso ON t."ServiceTrId"=tso."Id"
        JOIN "worker" w ON w."WorkerId"=tso."WorkerId"
        JOIN "user" u ON w."WorkerId"=u."UserId"
        JOIN "worker_service_company" wsc ON w."WorkerId"=wsc."WorkerId"
        JOIN "service_subcategory" ssc ON wsc."SCId"=ssc."SCId"
        WHERE ssc."Name"=%s;
        """
    testimonial_list = execute_sql_query(testimonial_list_query, params)

    service_session_query = """
        SELECT ssc."Name", ss."Price",  
        FROM service_session ss
        JOIN service_subcategory ssc ON ssc.SSCId = ss.SSCId
        """
    
    service_session_list = execute_sql_query(service_session_query, params)
    
    context = {
        "title" : "Sijarta Subcategory",
        "name_and_description" : name_and_description,
        "worker_list" : worker_list,
        "testimonial_list" : testimonial_list,
        "service_session_list" : service_session_list
    }
    
    # For debugging
    print(context)

    return render(request, "subcategory.html", context)


@login_required(login_url="/landingpage")
def customer_profile(request):
    context = {"title": "My Profile"}
    return render(request, "customer_profile.html", context)

@login_required(login_url="/landingpage")
def worker_profile(request):

    worker = request.GET.get('worker')
    worker_profile_query = """
        SELECT u."Username", w."Rate", w."TotalFinishOrder", u."PhoneNum", u"DoB", u."Address"
        FROM "user" u
        JOIN worker w ON w."WorkerId" = u."UserId"
        WHERE u."UserId" = %s
        """
    params = [worker]
    worker_profile_data = execute_sql_query(worker_profile_query, params)

    context = {
        "title": "My Profile",
        "worker_profile_data": worker_profile_data
    }

    return render(request, "worker_profile.html", context)

@login_required(login_url="/landingpage")
def mypay(request):
    # user_id = 'USR00' # should be based on request
    # Proposed solution:
    user_id = request.user
     
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


# TODO: Refactor to match the models
@login_required(login_url="/landingpage")
def mypay_transaction(request):
    current_user = request.user
    account = current_user.user_type.lower() # either user or worker
    
    if account == 'customer':
        categories = [
            ('top_up', 'Top Up MyPay'),
            ('service_payment', 'Service Payment'),
            ('transfer', 'Transfer MyPay'),
            ('withdrawal', 'Withdrawal'),
        ]
    elif account == 'worker':
        categories = [
            ('top_up', 'Top Up MyPay'),
            ('transfer', 'Transfer MyPay'),
            ('withdrawal', 'Withdrawal'),
        ]
    else:
        categories = []

    # get the selected transaction category from the dropdown
    selected_category = request.GET.get('category', None)  # Default to None
    # ensure selected category is one of the category options
    is_valid_category = any(selected_category == category[0] for category in categories)
    if not is_valid_category:
        selected_category = None

    form = None

    if selected_category == 'top_up':
        form = TopUpForm()
    elif selected_category == 'service_payment':
        # Fetch services
        services = [("1", "Service 1 - 500"), ("2", "Service 2 - 3000")]
        form = ServicePaymentForm()
        form.fields['service_session'].choices = services
    elif selected_category == 'transfer':
        form = TransferForm()
    elif selected_category == 'withdrawal':
        form = WithdrawalForm()

    context = {
               'form': form,
               'categories': categories,
               'selected_category': selected_category,
               'account': account
               }

    return render(request, "mypaytransaction.html", context)


@login_required(login_url="/landingpage")
def service_job(request):
    categories = {
            'service 1': ['1a', '1b'],
            'service 2': ['2a', '2b', '2c'],
    }
    subcategories = []

    selected_category = 'service 1';
    if selected_category in categories:
        subcategories = categories.get(selected_category, [])

    context = {"user": request.user,
               'categories': categories,
               'selected_category': selected_category,
               'subcategories': subcategories
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
    user_id = request.user.id  # Get logged-in user ID
    query = """
        SELECT 
            ssc."Name" AS SubcategoryName,
            ss."Session" AS SessionName,
            ss."Price" AS SessionPrice,
            wu."Username" AS WorkerName,
            os."Status" AS OrderStatus
        FROM 
            "user" u
        JOIN 
            "customer" c ON c."CustomerId" = u."UserId"
        JOIN 
            "orders" o ON o."CustomerId" = c."CustomerId"
        JOIN 
            "order_status" os ON os."OrderId" = o."OrderId"
        JOIN 
            "service_session" ss ON ss."SessionId" = o."SessionId"
        JOIN 
            "service_subcategory" ssc ON ssc."SSCId" = ss."SSCId"
        JOIN 
            "worker" w ON w."WorkerId" = ss."WorkerId"
        JOIN 
            "user" wu ON wu."UserId" = w."WorkerId"
        WHERE 
            u."UserId" = %s;
    """
    service_booking_list = execute_sql_query(query, user_id)
    context = {
        "title": "Sijarta Service Booking",
        "service_booking_list": service_booking_list    
    }
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
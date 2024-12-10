from django.shortcuts import render, redirect, get_object_or_404
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
from django.db import connection, IntegrityError, DatabaseError, InternalError
import json
import datetime
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
        "title": "Welcome to Sparklean",
        "last_login": request.COOKIES["last_login"],
    }
    return render(request, "home.html", context)

def register(request):
    context = {"title": "Registration Page"}
    return render(request, "register.html", context)

def register_customer(request):
    if request.method == 'POST':
        # Fetch the latest user ID from the database
        with connection.cursor() as cursor:
            cursor.execute("""SET search_path TO public; SELECT userid FROM "USER" ORDER BY userid DESC LIMIT 1;""")
            latest_user = cursor.fetchone()
            if latest_user:
                new_user_id = f"USR{int(latest_user[0][3:]) + 1:02d}"
            else:
                new_user_id = "USR01"  # Default for the first user

        # Get data from the POST request
        username = request.POST['username']
        sex = request.POST['sex']
        phonenum = request.POST['phonenum']
        password = make_password(request.POST['password'])
        birthdate = request.POST['birthdate']
        address = request.POST['address']

        try:
            with connection.cursor() as cursor:
                # Insert the new user into the USER table
                cursor.execute("""
                SET search_path TO public;
                INSERT INTO "USER" (userid, username, pwd, sex, phonenum, dob, address) 
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """, [new_user_id, username, password, sex, phonenum, birthdate, address])

                # Insert into the CUSTOMER table
                cursor.execute("""
                INSERT INTO CUSTOMER (customerid, level) VALUES (%s, %s);
                """, [new_user_id, 0])

            messages.success(request, "Customer registration successful!")
            return redirect('login_user')

        except Exception as e:
            messages.error(request, f"Error during registration: {str(e)}")
    
    return render(request, 'register_customer.html')


def register_worker(request):
    if request.method == 'POST':
        # Fetch the latest user ID from the database
        with connection.cursor() as cursor:
            cursor.execute("""SET search_path TO public; SELECT userid FROM "USER" ORDER BY userid DESC LIMIT 1;""")
            latest_user = cursor.fetchone()
            if latest_user:
                new_user_id = f"USR{int(latest_user[0][3:]) + 1:02d}"
            else:
                new_user_id = "USR01"  # Default for the first user

        # Get data from the POST request
        username = request.POST['username']
        sex = request.POST['sex']
        phonenum = request.POST['phonenum']
        password = make_password(request.POST['password'])
        birthdate = request.POST['birthdate']
        address = request.POST['address']

        # Additional fields for workers
        bankname = request.POST['bankname']
        accnumber = request.POST['accnumber']
        npwp = request.POST['npwp']
        picurl = request.POST['picurl']

        try:
            with connection.cursor() as cursor:
                # Insert the new user into the USER table
                cursor.execute("""
                SET search_path TO public;
                INSERT INTO "USER" (userid, username, pwd, sex, phonenum, dob, address) 
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """, [new_user_id, username, password, sex, phonenum, birthdate, address])

                # Insert into the WORKER table
                cursor.execute("""
                INSERT INTO WORKER (workerid, bankname, accnumber, npwp, picurl) 
                VALUES (%s, %s, %s, %s, %s);
                """, [new_user_id, bankname, accnumber, npwp, picurl])

            messages.success(request, "Worker registration successful!")
            return redirect('login_user')

        except Exception as e:
            messages.error(request, f"Error during registration: {str(e)}")

    return render(request, 'register_worker.html')


def login_user(request):
    if request.method == "POST":
        
        phonenum = request.POST['phonenum']
        checked_password = check_password(request.POST['password'])
        user = authenticate(request, phone_number=phonenum, password=checked_password)

        if user is not None:
            login(request, user)
            response = HttpResponseRedirect(reverse("main:show_main"))  
            response.set_cookie("last_login", str(datetime.datetime.now())) 
            return response
        else:
            messages.error(request, "Invalid phone number or password.")

    return render(request, "login.html")

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
        "title": "Sparklean Homepage",
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
    
    context = {"title": "Sparklean Subcategory"}
    return render(request, "subcategory.html", context)


@login_required(login_url="/landingpage")
def customer_profile(request):
    context = {"title": "My Profile"}
    return render(request, "customer_profile.html", context)

@login_required(login_url="/landingpage")
def worker_profile(request):
    context = {"title": "My Profile"}
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
        pass #form = TopUpForm()
    elif selected_category == 'service_payment':
        pass # Fetch services
        services = [("1", "Service 1 - 500"), ("2", "Service 2 - 3000")]
        pass #form = ServicePaymentForm()
        form.fields['service_session'].choices = services
    elif selected_category == 'transfer':
        pass #form = TransferForm()
    elif selected_category == 'withdrawal':
        pass #form = WithdrawalForm()

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
    context = {"title": "Sparklean Service Booking"}
    return render(request, "service_booking.html", context)


def create_testimonial(request):
    return render(request, "create_testimonial.html")


def discount(request):
    return render(request, "discount.html")

def myorder(request):
    return render(request, "myorder.html")

#@csrf_exempt
#def update_service_status(request, service_id):
    #if request.method == 'POST':
        #data = json.loads(request.body)
        #new_status = data.get('status')

        #try:
            # Update the service object in the database
            #service = Service.objects.get(id=service_id)
            #service.status = new_status
            #service.save()
            #return JsonResponse({'success': True})
        #xcept Service.DoesNotExist:
            #return JsonResponse({'success': False, 'error': 'Service not found'}, status=404)
    #return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def landingpage(request):
    return render(request, "landingpage.html")

def update_customer_profile(request):
    return render(request, "update_customer_profile.html")

def update_worker_profile(request):
    return render(request, "update_worker_profile.html")


@csrf_exempt
@login_required(login_url="/landingpage")
def update_customer_profile(request):
    userid = request.user.id

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        sex = request.POST.get('sex')
        phonenum = request.POST.get('phonenum')
        dob = request.POST.get('dob')
        address = request.POST.get('address')

        with connection.cursor() as cursor:
            # Update the customer details
            cursor.execute("""
            UPDATE "USER" 
            SET username = %s, sex = %s, phonenum = %s, dob = %s, address = %s
            WHERE userid = %s;
            """, [username, sex, phonenum, dob, address, userid])

            # Update password if provided
            if password:
                cursor.execute("""
                UPDATE "USER" 
                SET password = %s 
                WHERE userid = %s;
                """, [make_password(password), userid])

        messages.success(request, "Your profile has been updated successfully.")
        return redirect(reverse('main:customer-profile'))

    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT id, username, sex, phonenum, dob, address
        FROM "USER"
        WHERE userid = %s;
        """, [userid])
        user = cursor.fetchone()

    context = {
        'user': {
            'userid': user[0],
            'username': user[1],
            'sex': user[2],
            'phonenum': user[3],
            'dob': user[4],
            'address': user[5]
        }
    }
    return render(request, 'update_customer_profile.html', context)


@csrf_exempt
@login_required(login_url="/landingpage")
def update_worker_profile(request):
    userid = request.user.id

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        sex = request.POST.get('sex')
        phonenum = request.POST.get('phonenum')
        dob = request.POST.get('dob')
        address = request.POST.get('address')
        bankname = request.POST.get('bankname')
        accnumber = request.POST.get('accnumber')
        npwp = request.POST.get('npwp')
        picurl = request.POST.get('picurl')

        with connection.cursor() as cursor:
            # Update the worker's user details
            cursor.execute("""
            UPDATE "USER" 
            SET username = %s, sex = %s, phonenum = %s, dob = %s, address = %s
            WHERE userid = %s;
            """, [username, sex, phonenum, dob, address, userid])

            # Update password if provided
            if password:
                cursor.execute("""
                UPDATE "USER" 
                SET password = %s 
                WHERE userid = %s;
                """, [make_password(password), userid])

            # Update additional worker details
            cursor.execute("""
            UPDATE WORKER 
            SET bankname = %s, accnumber = %s, npwp = %s, picurl = %s
            WHERE id = %s;
            """, [bankname, accnumber, npwp, picurl, userid])

        messages.success(request, "Your profile has been updated successfully.")
        return redirect(reverse('main:worker-profile'))

    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT id, uname, sex, phonenum, dob, uaddress
        FROM "USER"
        WHERE id = %s;
        """, [userid])
        user = cursor.fetchone()

        cursor.execute("""
        SELECT bankname, accnumber, npwp, picurl
        FROM WORKER
        WHERE id = %s;
        """, [userid])
        worker = cursor.fetchone()

    context = {
        'user': {
            'id': user[0],
            'username': user[1],
            'sex': user[2],
            'phonenum': user[3],
            'dob': user[4],
            'address': user[5]
        },
        'worker': {
            'bank_name': worker[0],
            'acc_number': worker[1],
            'npwp': worker[2],
            'pic_url': worker[3]
        }
    }
    return render(request, 'update_worker_profile.html', context)


def worker_profile_summary(request):
    return render(request, "worker_profile_summary.html")
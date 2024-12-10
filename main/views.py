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
import uuid

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

        # Get data from POST request
        username = request.POST['username']
        sex = request.POST['sex']
        phonenum = request.POST['phonenum']
        password = make_password(request.POST['password'])
        dob = request.POST['dob']
        address = request.POST['address']
        new_userid = str(uuid.uuid4())

        try:
            with connection.cursor() as cursor:

                # Validate unique phone number
                query_string1 = """
                    SELECT COUNT(*)
                    FROM "user"
                    WHERE user.PhoneNum = %d
                """
                execute_sql_query(query_string1, [phonenum])

                if cursor.fetchone()[0] > 0:
                    messages.error(request, "Please use a different phone number, this phone number is registered already")
                    return render(request, 'register_customer.html')


                # Insert new user into USER table
                # query_string2 = (
                #     """
                #     SELECT phonenum
                #     FROM "user"
                #     WHERE phonenum = %d
                #     """
                # )
                
                query_string2="""
                INSERT INTO "USER" (userid, username, password, sex, phonenum, dob, address) 
                VALUES (%s, %s, %s, %s, %d, %s, %s);
                """
                params_2 = [new_userid, username, password, sex, phonenum, dob, address]

                execute_sql_query(query_string2, params_2)

                query_string3=  """
                INSERT INTO CUSTOMER (customerid, level) VALUES (%s, %d);
                """
                params_3 = [new_userid, 0]
                
                execute_sql_query(query_string3, params_3)

            messages.success(request, "Customer registration successful!")
            return redirect('login_user')

        except Exception as e:
            messages.error(request, f"Error during registration: {str(e)}")

    return render(request, 'register_customer.html')


def register_worker(request):
    if request.method == 'POST':
        
        # Fetch latest user ID from the database
        with connection.cursor() as cursor:
            cursor.execute("""SET search_path TO public; SELECT userid FROM "USER" ORDER BY userid DESC LIMIT 1;""")
            latest_user = cursor.fetchone()
            if latest_user:
                new_userid = f"USR{int(latest_user[0][3:]) + 1:02d}"
            else:
                new_userid = "USR01"  # Default for first user

        # Get data from POST request
        username = request.POST['username']
        sex = request.POST['sex']
        phonenum = request.POST['phonenum']
        password = make_password(request.POST['password'])
        dob = request.POST['dob']
        address = request.POST['address']

        # Specific workers attributes
        bankname = request.POST['bankname']
        accnumber = request.POST['accnumber']
        npwp = request.POST['npwp']
        picurl = request.POST['picurl']
        new_userid = str(uuid.uuid4())

        try:
            with connection.cursor() as cursor:
                # Validate unique phone number
                cursor.execute("""SET search_path TO public; SELECT COUNT(*) FROM "USER" WHERE phonenum = %s;""", [phonenum])
                if cursor.fetchone()[0] > 0:
                    messages.error(request, "Please use a different phone number, this phone number is registered already")
                    return render(request, 'register_worker.html')

                # Validate unique bank name and account number combination
                cursor.execute("""SET search_path TO public; SELECT COUNT(*) FROM WORKER WHERE bankname = %s AND accnumber = %s;""",
                               [bankname, accnumber])
                if cursor.fetchone()[0] > 0:
                    messages.error(request, "Please use a different bank name or account number")
                    return render(request, 'register_worker.html')

                # Insert the new user into the USER table
                cursor.execute("""
                SET search_path TO public;
                INSERT INTO "USER" (userid, username, password, sex, phonenum, dob, address) 
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """, [new_userid, username, password, sex, phonenum, dob, address])

                # Insert into the WORKER table
                cursor.execute("""
                INSERT INTO WORKER (workerid, bankname, accnumber, npwp, picurl) 
                VALUES (%s, %s, %s, %s, %s);
                """, [new_userid, bankname, accnumber, npwp, picurl])

            messages.success(request, "Worker registration successful!")
            return redirect('login_user')

        except Exception as e:
            messages.error(request, f"Error during registration: {str(e)}")

    return render(request, 'register_worker.html')


def login_user(request):
    if request.method == "POST":
        phonenum = request.POST.get('phonenumber')
        password = request.POST.get('password')

        # Ensure both fields are provided
        if not phonenum or not password:
            messages.error(request, "Phone number and password are required.")
            return render(request, "login.html")

        try:
            # Validate phone number and password
            query = """SELECT "UserId", "Password" FROM "user" WHERE "PhoneNum" = %s;"""
            user_data = execute_sql_query(query, [phonenum])
            print(user_data)
            if user_data:
                user_id, stored_password = user_data[0]['UserId'], user_data[0]['Password']
                print(user_id, stored_password)
                if str(password) == str(stored_password):
                    print("pass 1")
                    # Determine user type (customer or worker)
                    query_user_type = """SELECT "CustomerId" FROM "customer" WHERE "CustomerId" = %s;"""
                    user_type_result = execute_sql_query(query_user_type, [user_id])
                    user_type = "customer" if user_type_result else "worker"
                    # Log in user and set cookies
                    request.session["is_authenticated"] = True
                    print("pass 2")
                    request.session["user_id"] = user_id
                    request.session["user_type"] = user_type
                    
                    # Simulated login
                    login(request, user_id)

                    # Set cookie for last login
                    response = HttpResponseRedirect(reverse("main:show_main"))
                    response.set_cookie("last_login", str(datetime.datetime.now()))

                    return response
                else:
                    messages.error(request, "Invalid phone number or password.")
            else:
                messages.error(request, "Invalid phone number or password.")
                
        except Exception as e:
            messages.error(request, f"An error occurred during login: {str(e)}")
        
    return render(request, "login.html")

# def login_user(request):
#     if request.method == "POST":
#         phonenum = request.POST.get('phonenum')
#         password = request.POST.get('password')

#         # Ensure both fields are provided
#         if not phonenum or not password:
#             messages.error(request, "Phone number and password are required.")
#             return render(request, "login.html")

#         try:
#             with connection.cursor() as cursor:
#                 # Validate phone number and password
#                 query="""   
#                     SELECT userid, password FROM "User" WHERE phonenum = %s;
#                     """
#                 user_data = execute_sql_query(query)

#                 if user_data and check_password(password, user_data[1]):
#                     user_id = user_data[0]

#                     # Determine the user type
#                     cursor.execute(
#                         """SET search_path TO public;
#                         SELECT customerid FROM CUSTOMER WHERE customerid = %s;""",
#                         [user_id]
#                     )
#                     is_customer = cursor.fetchone()

#                     if is_customer:
#                         user_type = 'customer'
#                     else:
#                         user_type = 'worker'

#                     # Log in user and set cookies
#                     request.session['is_authenticated'] = True
#                     request.session['user_id'] = user_id
#                     request.session['user_type'] = user_type
#                     login(request, user_id)  # Simulated login
#                     response = HttpResponseRedirect(reverse("main:show_main"))
#                     response.set_cookie("last_login", str(datetime.datetime.now()))
#                     return response
#                 else:
#                     # Invalid credentials
#                     messages.error(request, "Invalid phone number and password.")

#         except Exception as e:
#             messages.error(request, f"An error occurred during login: {str(e)}")
#             return render(request, "login.html")

#     return render(request, "login.html")


def logout_user(request):
    request.session.flush()
    return redirect("main:landingpage")

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
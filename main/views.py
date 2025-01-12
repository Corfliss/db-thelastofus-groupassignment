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

@csrf_exempt
def execute_sql_query(query, params=None):
    """Helper function to execute raw SQL queries."""
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        if cursor.description:  # Check if the query returns data
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
        return None

@csrf_exempt
def execute_sql_query(query, params=None):
    """Helper function to execute raw SQL queries."""
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        if cursor.description:  # Check if the query returns data
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
        return None

@csrf_exempt
def show_main(request):

    # Blocks users that are not logged in from accessing
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('main:landingpage')
    
    try:
        last_login = request.COOKIES["last_login"]
    except:
        last_login = "No last login"
    context = {
        "last_login": last_login,
    }
    return render(request, "home.html", context)

@csrf_exempt
def landingpage(request):
    return render(request, "landingpage.html")


# yellow features #
# register #

@csrf_exempt
def register(request):
    context = {"title": "Registration Page"}
    return render(request, "register.html", context)

@csrf_exempt
def register_customer(request):
    if request.method == "POST":

        # Get data from POST request
        username = request.POST["username"]
        sex = request.POST["sex"]
        phonenum = request.POST["phonenum"]
        password = request.POST["password"]
        dob = request.POST["dob"]
        address = request.POST["address"]
        n_userid = uuid.uuid4().hex
        new_userid = str(n_userid)

        try:
            with connection.cursor() as cursor:

                user_insert = """
                INSERT INTO "user" ("UserId", "Username", "Password", "Sex", "PhoneNum", "DoB", "Address") 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                params_2 = [new_userid, username, password, sex, phonenum, dob, address]

                execute_sql_query(user_insert, params_2)

                customer_insert = """
                INSERT INTO "customer" ("CustomerId", "Level")
                VALUES (%s, %s)
                """
                params_3 = [new_userid, 0]

                execute_sql_query(customer_insert, params_3)

            messages.success(request, "Customer registration successful!")
            return redirect("main:login")

        except Exception as e:
            messages.error(request, f"Error during registration: {str(e)}")

    return render(request, "register_customer.html")

@csrf_exempt
def register_worker(request):
    if request.method == "POST":

        # Get data from POST request
        username = request.POST["username"]
        sex = request.POST["sex"]
        phonenum = request.POST["phonenum"]
        password = request.POST["password"]
        dob = request.POST["dob"]
        address = request.POST["address"]
        bankname = request.POST["bankname"]
        accnumber = request.POST["accnumber"]
        npwp = request.POST["npwp"]
        picurl = request.POST["picurl"]
        n_userid = uuid.uuid4().hex
        new_userid = str(n_userid)

        try:
            with connection.cursor() as cursor:

                user_insert = """
                INSERT INTO "user" ("UserId", "Username", "Password", "Sex", "PhoneNum", "DoB", "Address") 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                params_2 = [new_userid, username, password, sex, phonenum, dob, address]

                execute_sql_query(user_insert, params_2)

                worker_insert = """
                INSERT INTO "worker" ("WorkerId", "BankName", "AccNumber", "NPWP", "PicURL", "Rate", "TotalFinishOrder")
                VALUES (%s, %s, %s, %s, %s,  %s, %s)
                """
                params_3 = [new_userid, bankname, accnumber, npwp, picurl, 0, 0]

                execute_sql_query(worker_insert, params_3)

            messages.success(request, "Worker registration successful!")
            return redirect("main:login")

        except Exception as e:
            messages.error(request, f"Error during registration: {str(e)}")

    return render(request, "register_worker.html")


## login ##

@csrf_exempt
def login_user(request):
    if request.method == "POST":
        phonenum = request.POST.get("phonenumber")
        password = request.POST.get("password")

        # Validation for input
        if not phonenum or not password:
            messages.error(request, "Phone number and password are required.")
            return render(request, "login.html")

        try:

            query = """SELECT "UserId", "Username", "Password" FROM "user" WHERE "PhoneNum" = %s;"""
            user_data = execute_sql_query(query, [phonenum])
            print(user_data)
            if user_data:
                user_id, stored_password = (
                    user_data[0]["UserId"],
                    user_data[0]["Password"],
                )
                print(user_id, stored_password)
                if str(password) == str(stored_password):
                    print("pass 1")

                    # User type assignment
                    query_user_type = """SELECT "CustomerId" FROM "customer" WHERE "CustomerId" = %s;"""
                    user_type_result = execute_sql_query(query_user_type, [user_id])
                    user_type = "customer" if user_type_result else "worker"

                    # Username retrieval
                    username = user_data[0]["Username"]

                    # Set session
                    request.session["is_authenticated"] = True
                    print("pass 2")
                    request.session["user_id"] = user_id
                    request.session["user_type"] = user_type
                    request.session["username"] = username

                    # Set cookie
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


## logout ##
@csrf_exempt
def logout_user(request):
    request.session.flush()
    return redirect("main:landingpage")


## profile ##
@csrf_exempt
def customer_profile(request):

    # Blocks users that are not logged in from accessing
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('main:landingpage')
    

    try:
        user_id = request.session.get("user_id")

        full_user_query = """
            SELECT "UserId", "Username", "Sex", "PhoneNum", "DoB", "Address", "MyPayBalance"
            FROM "user"
            WHERE "UserId" = %s
        """
        params = [user_id]
        user_bio = execute_sql_query(full_user_query, params)

        customer_query = """
            SELECT "CustomerId", "Level"
            FROM customer
            WHERE "CustomerId" = %s
        """
        params = [user_id]
        customer_bio = execute_sql_query(customer_query, params)

        context = {
            "user": request.user,
            "user_info": user_bio[0],
            "customer_info": customer_bio[0],
        }

        return render(request, "customer_profile.html", context)

    except Exception as e:
        print(f"Error in worker_profile view: {e}")
        return HttpResponse("An error occured.")

@csrf_exempt
def worker_profile(request):

    # Blocks users that are not logged in from accessing
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('main:landingpage')

    try:
        user_id = request.session["user_id"]

        full_user_query = """
            SELECT "UserId", "Username", "Sex", "PhoneNum", "DoB", "Address", "MyPayBalance"
            FROM "user"
            WHERE "UserId" = %s
        """
        params = [user_id]
        user_bio = execute_sql_query(full_user_query, params)

        worker_query = """
            SELECT "WorkerId", "BankName", "AccNumber", "NPWP", "PicURL", "Rate", "TotalFinishOrder"
            FROM worker
            WHERE "WorkerId" = %s
        """
        params = [user_id]
        worker_bio = execute_sql_query(worker_query, params)

        context = {
            "user": request.user,
            "user_info": user_bio[0],
            "worker_info": worker_bio[0],
        }

        return render(request, "worker_profile.html", context)

    except Exception as e:
        print(f"Error in worker_profile view: {e}")
        return HttpResponse("An error occured.")


## update profile ##
@csrf_exempt
def update_customer_profile(request):

    # Blocks users that are not logged in from accessing
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('main:landingpage')

    if request.method == "POST":

        # Get data from POST request
        username = request.POST["username"]
        sex = request.POST["sex"]
        phonenum = request.POST["phonenum"]
        password = request.POST["password"]
        dob = request.POST["dob"]
        address = request.POST["address"]
        new_userid = request.session.get("user_id")

        try:
            with connection.cursor() as cursor:
                # Update user data
                user_update = """
                UPDATE "user"
                SET "Username" = %s, "Password" = %s, "Sex" = %s, "PhoneNum" = %s, "DoB" = %s, "Address" = %s
                WHERE "UserId" = %s
                """
                params_user = [
                    username,
                    password,
                    sex,
                    phonenum,
                    dob,
                    address,
                    new_userid,
                ]
                cursor.execute(user_update, params_user)

            messages.success(request, "Customer profile updated successfully!")
            return redirect("main:customer-profile")

        except Exception as e:
            error_message = f"Error during profile update: {str(e)}"
            print(error_message)
            messages.error(request, error_message)
            return redirect("main:update-customer-profile")

    return render(request, "update_customer_profile.html")

@csrf_exempt
def update_worker_profile(request):

    # Blocks users that are not logged in from accessing
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('main:landingpage')

    if request.method == "POST":

        # Get data from POST request
        username = request.POST["username"]
        sex = request.POST["sex"]
        phonenum = request.POST["phonenum"]
        password = request.POST["password"]
        dob = request.POST["dob"]
        address = request.POST["address"]
        bankname = request.POST["bankname"]
        accnumber = request.POST["accnumber"]
        npwp = request.POST["npwp"]
        picurl = request.POST["picurl"]
        new_userid = request.session.get("user_id")

        try:
            with connection.cursor() as cursor:
                # Update user data
                user_update = """
                UPDATE "user"
                SET "Username" = %s, "Password" = %s, "Sex" = %s, "PhoneNum" = %s, "DoB" = %s, "Address" = %s
                WHERE "UserId" = %s
                """
                params_user = [
                    username,
                    password,
                    sex,
                    phonenum,
                    dob,
                    address,
                    new_userid,
                ]
                cursor.execute(user_update, params_user)

                # Update worker data
                worker_update = """
                UPDATE "worker"
                SET "BankName" = %s, "AccNumber" = %s, "NPWP" = %s, "PicURL" = %s
                WHERE "WorkerId" = %s
                """
                params_worker = [bankname, accnumber, npwp, picurl, new_userid]
                cursor.execute(worker_update, params_worker)

            messages.success(request, "Worker profile updated successfully!")
            return redirect("main:worker-profile")

        except Exception as e:
            error_message = f"Error during profile update: {str(e)}"
            print(error_message)
            messages.error(request, error_message)
            return redirect("main:update-worker-profile")

    return render(request, "update_worker_profile.html")


## green features ##
# homepage #
@csrf_exempt
def home(request):

    # Blocks users that are not logged in from accessing
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('main:landingpage')
    
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

@csrf_exempt
def home(request):

    # Blocks users that are not logged in from accessing
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('main:landingpage')
    

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
        category_id = row["categoryid"]
        if category_id not in category_subcategory_dict:
            category_subcategory_dict[category_id] = {
                "name": row["categoryname"],
                "subcategories": [],
            }

        category_subcategory_dict[category_id]["subcategories"].append(
            {
                "name": row["subcategoryname"],
                "description": row["subcategorydescription"],
            }
        )

    context = {
        "title": "Sijarta Homepage",
        "user": user,
        "categories": category_subcategory_dict,
    }

    # For debugging purpose
    # print(category_subcategory_result)
    return render(request, "home.html", context)

@csrf_exempt
def worker_profile_summary(request):

    # Blocks users that are not logged in from accessing
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('main:landingpage')
    
    return render(request, "worker_profile_summary.html")


# service booking #
@csrf_exempt
def service_booking(request):

    # Blocks users that are not logged in from accessing
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('main:landingpage')
    

    user_id = request.session.get("user_id")

    user_query = """
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
    params = [user_id]
    service_booking_list = execute_sql_query(user_query, params)

    context = {
        "service_booking_list": service_booking_list,
    }

    return render(request, "service_booking.html", context)


# subcategory #
@csrf_exempt
def subcategory(request):

    # Blocks users that are not logged in from accessing
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('main:landingpage')
    

    # This might break the code, if anyone know better, glad to see the fix
    subcategory_name = request.GET.get("subcategory_id")

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
        "title": "Sijarta Subcategory",
        "name_and_description": name_and_description,
        "worker_list": worker_list,
        "testimonial_list": testimonial_list,
        "service_session_list": service_session_list,
    }
    return render(request, "subcategory.html", context)

@csrf_exempt
def myorder(request):

    # Blocks users that are not logged in from accessing
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('main:landingpage')
    
    return render(request, "myorder.html")


# update order status #
@csrf_exempt
def update_order_status(request, order_id):

    # Blocks users that are not logged in from accessing
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('main:landingpage')

    next_status_mapping = {"STI04": "STI06", "STI06": "STI05", "STI05": "STI00"}

    # Fetch current status
    current_status_query = """
        SELECT os."Status", os."StatusId"
        FROM TR_ORDER_STATUS tos
        JOIN ORDER_STATUS os ON tos."StatusId" = os."StatusId"
        WHERE tos."ServiceTrId" = %s
        ORDER BY tos."date" DESC
    """
    current_status = execute_sql_query(current_status_query, [order_id])
    current_status = current_status[0]["StatusId"]

    # Determine the next status
    next_status = next_status_mapping.get(current_status)
    if not next_status:
        print("No next status")
        return redirect("main:service-job-status")  # No valid next status

    # Update the order status
    update_status_query = """
                    UPDATE tr_order_status 
                    SET "StatusId" = %s
                    WHERE "ServiceTrId" = %s
                    """
    params = [next_status, order_id]
    execute_sql_query(update_status_query, params)
    print("Updated the order status")
    return redirect("main:service-job-status")


## blue features ##
# Testimony R
@csrf_exempt
def view_testimony(request):

    user_id = request.user
    user_query = "SELECT * FROM testimony"
    query_result = execute_sql_query(user_query)
    context = {"user": user_id, "testimonies": query_result}
    return render(request, "subcategory.html", context)

@csrf_exempt
def create_testimonial(request):
    return render(request, "create_testimonial.html")


# discount #
@csrf_exempt
def discount(request):

    # Blocks users that are not logged in from accessing
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('main:landingpage')

    voucher_query = """
        SELECT v."Code","MinTrOrder", "NmbDayValid", "UserQuota", "Price", "Discount" 
        FROM voucher v 
        JOIN discount d
        ON v."Code" = d."Code"
    """
    promo_query = """
        SELECT "Code", "OfferEndDate" FROM promo
    """
    voucher_results = execute_sql_query(voucher_query)
    promo_results = execute_sql_query(promo_query)
    context = {
        "user": request.user,
        "vouchers": voucher_results,
        "promo": promo_results,
    }
    return render(request, "discount.html", context)


# voucher
@csrf_exempt
def purchase_voucher(request):

    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to make a purchase.")
        return redirect("discount")  # Redirect to the discount page

    if request.method == "POST":
        user_id = request.user.id
        voucher_code = request.POST.get("voucher_code")
        voucher_price = float(request.POST.get("voucher_price"))

        # Get the user's current balance
        user_balance_query = """
        SELECT "Nominal" FROM "tr_mypay" WHERE "UserId" = %s
        """
        user_balance_results = execute_sql_query(user_balance_query, [user_id])
        user_balance = user_balance_results[0]["Nominal"] if user_balance_results else 0

        if user_balance < voucher_price:
            messages.error(request, "Insufficient balance to purchase this voucher.")
            return redirect("discount")

        # Deduct the voucher price from the user's balance
        update_balance_query = """
        UPDATE "tr_mypay"
        SET "Nominal" = "Nominal" - %s
        WHERE "UserId" = %s
        """
        execute_sql_query(update_balance_query, [voucher_price, user_id])

        # Optionally: Insert a record into a table to log the purchase
        insert_purchase_query = """
        INSERT INTO "user_voucher" ("UserId", "VoucherCode", "PurchaseDate")
        VALUES (%s, %s, NOW())
        """
        execute_sql_query(insert_purchase_query, [user_id, voucher_code])

        messages.success(request, "Voucher purchased successfully!")
        return HttpResponse("Voucher purchased successfully.")
    return HttpResponse("Invalid request.")


## red features ##
@csrf_exempt
def mypay(request):

    # Blocks users that are not logged in from accessing
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('main:landingpage')

    user_id = request.session["user_id"]

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


# mypay transaction #
@csrf_exempt
def mypay_transaction(request):

    user_id = request.session["user_id"]
    account = None

    # try to query userid in customer
    customer_query = """
        SELECT *
        FROM customer
        WHERE "CustomerId" = %s
    """
    customer_result = execute_sql_query(customer_query, [user_id])
    print("customer result: ", customer_result)
    if len(customer_result) > 0:
        account = "customer"

    # else try to query userid in worker
    else:
        worker_query = """
            SELECT *
            FROM worker
            WHERE "WorkerId" = %s
        """
        worker_result = execute_sql_query(worker_query, [user_id])
        print("worker result: ", worker_result)
        if len(worker_result) > 0:
            account = "worker"

    # if doesn't exist, then user neither customer nor worker
    '''
    update_query = """
                    UPDATE tr_order_status 
                    SET "StatusId" = %s
                    WHERE "ServiceTrId" = %s
                    """
    params = ["STI02", "STI00"]
    result = execute_sql_query(update_query, params)
    '''
    # organize the service categories
    categories = []
    services = []
    if account == "customer":
        categories = [
            ("Top Up"),
            ("Service Payment"),
            ("Transfer"),
            ("Withdrawal"),
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

    elif account == "worker":
        categories = [
            ("Top Up"),
            ("Transfer"),
            ("Withdrawal"),
        ]
    else:
        categories = []

    context = {"states": categories, "services": services}

    if request.method == "POST":
        print("POST request triggered")

        state = request.POST.get("state")

        try:
            # Handle each state
            if state == "Top Up":
                print("MyPay Top Up")
                try:
                    amount = float(request.POST.get("top_up_amount"))
                except:
                    raise ValueError("Top-up amount must be a number.")
                if amount <= 0:
                    raise ValueError("Top-up amount must be positive.")

                # increase user's MyPay balance
                query = """
                    UPDATE "user"
                    SET "MyPayBalance" = "MyPayBalance" + %s
                    WHERE "UserId" = %s
                """
                execute_sql_query(query, [amount, user_id])

                # Add transaction to tr_mypay
                query = """
                    INSERT INTO tr_mypay ("UserId", "Date", "Nominal", "CategoryId")
                    VALUES (%s, CURRENT_DATE, %s, %s)
                """
                params = [user_id, amount, "MPC00"]
                execute_sql_query(query, params)

            elif state == "Service Payment":
                service_id = request.POST.get("service_id")
                amount_due = float(request.POST.get("service_price"))
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
                    if balance[0]["MyPayBalance"] < amount_due:
                        raise ValueError("Insufficient MyPay balance.")

                    # withdraw amount from user for service
                    query = """
                        UPDATE "user"
                        SET "MyPayBalance" = "MyPayBalance" - %s
                        WHERE "UserId" = %s
                    """
                    execute_sql_query(query, [amount_due, user_id])

                    # Add transaction to tr_mypay
                    query = """
                        INSERT INTO tr_mypay ("UserId", "Date", "Nominal", "CategoryId")
                        VALUES (%s, CURRENT_DATE, %s, %s)
                    """
                    params = [user_id, -amount_due, "MPC01"]
                    execute_sql_query(query, params)

                # set service status as looking for worker
                update_query = """
                    UPDATE tr_order_status 
                    SET "StatusId" = %s
                    WHERE "ServiceTrId" = %s
                    """
                params = ["STI03", service_id]
                result = execute_sql_query(update_query, params)

            elif state == "Transfer":
                print("MyPay Transfer")
                recipient_phone = request.POST.get("recipient_phone")
                try:
                    amount = float(request.POST.get("transfer_amount"))
                except:
                    raise ValueError("Transfer amount must be a number.")
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
                if balance[0]["MyPayBalance"] < amount:
                    raise ValueError("Insufficient balance.")

                # Deduct from sender
                deduct_query = """
                    UPDATE "user"
                    SET "MyPayBalance" = "MyPayBalance" - %s
                    WHERE "UserId" = %s
                """
                execute_sql_query(deduct_query, [amount, user_id])

                # Add transaction to tr_mypay of sender
                query = """
                    INSERT INTO tr_mypay ("UserId", "Date", "Nominal", "CategoryId")
                    VALUES (%s, CURRENT_DATE, %s, %s)
                """
                params = [user_id, -amount, "MPC02"]
                execute_sql_query(query, params)

                # Add to recipient
                add_query = """
                    UPDATE "user"
                    SET "MyPayBalance" = "MyPayBalance" + %s
                    WHERE "PhoneNum" = %s
                """
                execute_sql_query(add_query, [amount, recipient_phone])

                # Add transaction to tr_mypay of recipient
                query = """
                    INSERT INTO tr_mypay ("UserId", "Date", "Nominal", "CategoryId")
                    VALUES (%s, CURRENT_DATE, %s, %s)
                """
                params = [recipient_id, amount, "MPC00"]
                execute_sql_query(query, params)

            elif state == "Withdrawal":
                print("MyPay Withdrawal")
                bank_name = request.POST.get("bank_name")
                account_number = request.POST.get("bank_account")

                try:
                    withdrawal_amount = float(request.POST.get("withdrawal_amount"))
                except:
                    raise ValueError("Withdrawal amount must be a number.")
                if withdrawal_amount <= 0:
                    raise ValueError("Withdrawal amount must be positive.")

                # Check if sender has enough funds
                balance_query = """
                    SELECT "MyPayBalance" 
                    FROM "user"
                    WHERE "UserId" = %s
                    """
                balance = execute_sql_query(balance_query, [user_id])
                if balance[0]["MyPayBalance"] < withdrawal_amount:
                    raise ValueError("Insufficient balance.")

                deduct_query = """
                    UPDATE "user"
                    SET "MyPayBalance" = "MyPayBalance" - %s
                    WHERE "UserId" = %s
                """
                execute_sql_query(deduct_query, [withdrawal_amount, user_id])

                # Add transaction to tr_mypay
                query = """
                    INSERT INTO tr_mypay ("UserId", "Date", "Nominal", "CategoryId")
                    VALUES (%s, CURRENT_DATE, %s, %s)
                """
                params = [user_id, -withdrawal_amount, "MPC04"]
                execute_sql_query(query, params)

            messages.success(request, "Transaction successful!")

        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, "mypaytransaction.html", context)


# service job
@csrf_exempt
def service_job(request):

    # Blocks users that are not logged in from accessing
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('main:landingpage')

    user_id = request.session["user_id"]
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
    if request.method == "POST" and "search" in request.POST:
        print("search activated")
        category_id = request.POST.get("category")
        subcategory_id = request.POST.get("subcategory")

        if subcategory_id:
            services_query = """
                SELECT tso."Id" as "OrderId", tso."TotalPrice", tso."OrderDate", tso."Session", u."Username", ss."Name" AS "ServiceName"
                FROM tr_service_order tso
                JOIN tr_order_status tos ON tso."Id" = tos."ServiceTrId"
                JOIN "user" u ON tso."CustomerId" = u."UserId"
                JOIN service_subcategory ss ON tso."ServiceCategoryId" = ss."SSCId"
                WHERE tso."ServiceCategoryId" = %s AND tos."StatusId" = %s
            """
            params = [subcategory_id, "STI03"]
            services = execute_sql_query(services_query, params)

        elif category_id:

            services_query = """
                SELECT tso."Id", tso."TotalPrice", tso."OrderDate", tso."Session", u."Username", ss."Name" AS "ServiceName"
                FROM tr_service_order tso
                JOIN tr_order_status tos ON tso."Id" = tos."ServiceTrId"
                JOIN "user" u ON tso."CustomerId" = u."UserId"
                JOIN service_subcategory ss ON tso."ServiceCategoryId" = ss."SSCId"
                WHERE ss."SCId" = %s AND tos."StatusId" = %s
                """
            params = [category_id, "STI03"]
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
            params = [user_id, "STI03"]
            services = execute_sql_query(services_query, params)

        print(services)

    # Handle Accept Order action
    if request.method == "POST" and "accept_order" in request.POST:
        order_id = request.POST["accept_order"]

        # validate that order still exists as looking for workers
        order_query = """
                    SELECT o."Id", o."Session"
                    FROM tr_service_order o
                    JOIN tr_order_status tos ON o."Id" = tos."ServiceTrId"
                    WHERE o."Id" = %s AND tos."StatusId" = %s
                    """
        params = [order_id, "STI03"]
        order = execute_sql_query(order_query, params)
        print(order_id)

        if len(order) == 0:
            raise ValueError("Cannot accept this service.")
        session = order[0]["Session"]

        # change the status to waiting for worker
        update_query = """
                    UPDATE tr_order_status 
                    SET "StatusId" = %s
                    WHERE "ServiceTrId" = %s
                    """
        params = ["STI04", order_id]
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
        "categories": categories,
        "subcategories": subcategories,
        "services": services,
    }
    return render(request, "servicejob.html", context)


# service job status
@csrf_exempt
def service_job_status(request):

    # Blocks users that are not logged in from accessing
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('main:landingpage')
    
    # Update the order status where needed
    '''
    update_status_query = """
                    UPDATE order_status
                    SET "Status" = %s
                    WHERE "StatusId" = %s
                    """
    params = ['Waiting for Worker to Depart', 'STI04']
    execute_sql_query(update_status_query, params)
    update_status_query = """
                    UPDATE order_status
                    SET "Status" = %s
                    WHERE "StatusId" = %s
                    """
    params = ['Service in Progress', 'STI05']
    execute_sql_query(update_status_query, params)

    update_status_query = """
                    INSERT INTO order_status VALUES
                    (%s, %s)
                    """
    params = ['STI06', 'Worker Arrived at Location']
    execute_sql_query(update_status_query, params)

    # show all statuses
    select_status_query = """
                    SELECT * FROM order_status
                    """
    result = execute_sql_query(select_status_query, [])
    print(result)
    '''

    '''
    update_status_query = """
                    UPDATE tr_order_status 
                    SET "StatusId" = %s
                    WHERE "ServiceTrId" = %s
                    """
    params = ['STI04', 'STI00']
    execute_sql_query(update_status_query, params)
    '''

    user_id = request.session["user_id"]
    filter_status = request.GET.get("status", "")
    filter_order_name = request.GET.get("order_name", "")

    # Fetch all orders for the current worker with optional filters
    orders_query = """
        SELECT tso."Id", tso."OrderDate", tso."Session", tso."TotalPrice", tso."CustomerId", 
            os."Status", os."StatusId", 
            ss."Name" AS "ServiceName",
            u."Username"
        FROM TR_SERVICE_ORDER tso
        JOIN TR_ORDER_STATUS tos ON tso."Id" = tos."ServiceTrId"
        JOIN ORDER_STATUS os ON tos."StatusId" = os."StatusId"
        JOIN service_subcategory ss ON tso."ServiceCategoryId" = ss."SSCId"
        JOIN "user" u ON tso."CustomerId" = u."UserId"
        WHERE tso."WorkerId" = %s
        AND (%s = '' OR os."Status" = %s)
        AND (%s = '' OR ss."Name" ILIKE %s)
        ORDER BY tso."OrderDate" DESC
    """
    params = [
        user_id,
        filter_status,
        filter_status,
        filter_order_name,
        f"%{filter_order_name}%",
    ]
    orders = execute_sql_query(orders_query, params)

    context = {
        "orders": orders,
        "statuses": [
            "Waiting for Worker to Depart",
            "Worker Arrived at Location",
            "Service in Progress",
            "Order Completed",
            "Order Canceled",
        ],
        "filter_status": filter_status,
        "filter_order_name": filter_order_name,
    }

    return render(request, "servicejobstatus.html", context)

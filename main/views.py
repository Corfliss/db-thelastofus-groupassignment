from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.core import serializers
from .forms import TopUpForm, ServicePaymentForm, TransferForm, WithdrawalForm

import datetime


@login_required(login_url="/login")
def show_main(request):
    context = {
        "title": "Welcome to Sijarta",
        "last_login": request.COOKIES["last_login"],
    }
    return render(request, "main.html", context)


def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been successfully created!")
            return redirect("main:login")
    context = {"form": form}
    return render(request, "register.html", context)


def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            response = HttpResponseRedirect(reverse("main:show_main"))
            response.set_cookie("last_login", str(datetime.datetime.now()))
            return response
    else:
        form = AuthenticationForm()  # Ensure form is initialized for GET requests

    context = {"form": form}
    return render(request, "login.html", context)


def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse("main:login"))
    response.delete_cookie("last_login")
    return response


def home(request):
    context = {"title": "Sijarta Homepage"}
    return render(request, "home.html", context)


def subcategory(request):
    context = {"title": "Sijarta Subcategory"}
    return render(request, "subcategory.html", context)


@login_required(login_url="/login")
def profile(request):
    context = {"title": "Sijarta Profile"}
    return render(request, "profile.html", context)


@login_required(login_url="/login")
def mypay(request):
    past_transactions = [
        {"amount": "+50.00", "date": "2024-11-01", "category": "Deposit"},
        {"amount": "-30.00", "date": "2024-11-05", "category": "Withdrawal"},
        {"amount": "+100.00", "date": "2024-11-10", "category": "Deposit"},
    ]

    context = {
        "user": request.user,
        "phone_number": "123-456-789",
        "balance": 12000,
        "transactions": past_transactions,
    }

    return render(request, "mypay.html", context)


@login_required(login_url="/login")
def mypay_transaction(request):
    account = 'worker' # either user or worker
    
    if account == 'user':
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


@login_required(login_url="/login")
def service_job(request):
    context = {"user": request.user}

    return render(request, "servicejob.html", context)


def service_job_status(request):
    context = {"user": request.user}

    return render(request, "servicejobstatus.html", context)


def service_booking(request):
    context = {"title": "Sijarta Service Booking"}
    return render(request, "service_booking.html", context)


def create_testimonial(request):
    return render(request, "create_testimonial.html")


def discount(request):
    return render(request, "discount.html")

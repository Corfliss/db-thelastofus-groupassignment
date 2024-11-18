from django.urls import path
from . import views
from main.views import (
    show_main,
    register,
    login_user,
    logout_user,
    home,
    subcategory,
    profile,
    service_booking,
    mypay,
    mypay_transaction,
    service_job,
    service_job_status,
    create_testimonial,
    discount,
    myorder,
    landingpage,
    register_customer,
    register_worker,

)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("home/", home, name="home"),
    path("subcategory/", subcategory, name="subcategory"),
    path("profile/", profile, name="profile"),
    path("mypay/", mypay, name="mypay"),
    path("mypay-transaction/", mypay_transaction, name="mypay-transaction"),
    path("service-job/", service_job, name="service-job"),
    path("service-job-status/", service_job_status, name="service-job-status"),
    path("service_booking/", service_booking, name="service_booking"),
    path("create_testimonial/", create_testimonial, name="create_testimonial"),
    path("discount/", discount, name="discount"),
    path("myorder/", myorder, name="my-orcer"),
    path('landingpage/', landingpage, name='landingpage'),
    path('register_worker/', register_worker, name='register_worker'),
    path('register_customer/', register_customer, name='register_customer'),
]

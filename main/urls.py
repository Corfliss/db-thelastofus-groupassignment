from django.urls import path
from . import views
from main.views import (
    show_main,
    register,
    login_user,
    logout_user,
    home,
    subcategory,
    customer_profile,
    worker_profile,
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
    update_customer_profile,
    update_worker_profile,
    worker_profile_summary,
    update_order_status
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("home/", views.home, name="home"),
    path("subcategory/", subcategory, name="subcategory"),
    path("customer-profile/", customer_profile, name="customer-profile"),
    path("worker-profile/", worker_profile, name="worker-profile"),
    path("worker-profile-summary/", worker_profile_summary, name="worker-profile-summary"),
    path("update-customer-profile/", update_customer_profile, name="update-customer-profile"),
    path("update-worker-profile/", update_worker_profile, name="update-worker-profile"),
    path("mypay/", mypay, name="mypay"),
    path("mypay-transaction/", mypay_transaction, name="mypay-transaction"),
    path("service-job/", service_job, name="service-job"),
    path("service-job-status/", service_job_status, name="service-job-status"),
    path('service-job-status/update-status/<str:order_id>/', update_order_status, name='update_order_status'),
    path("service_booking/", service_booking, name="service_booking"),
    path("create_testimonial/", create_testimonial, name="create_testimonial"),
    path("discount/", discount, name="discount"),
    path("myorder/", myorder, name="my-orcer"),
    path('landingpage/', landingpage, name='landingpage'),
    path('register_worker/', register_worker, name='register_worker'),
    path('register_customer/', register_customer, name='register_customer'),
    
]

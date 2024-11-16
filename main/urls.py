from django.urls import path
from main.views import show_main, register, login_user, logout_user, home, subcategory, profile, service_booking, mypay, mypay_transaction, service_job, service_job_status

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('home/', home, name='home'),
    path('subcategory/', subcategory, name='subcategory'),
    path('profile/', profile, name='profile'),
    path('mypay/', mypay, name='mypay'),
    path('mypay-transaction/', mypay_transaction, name='mypay-transaction'),
    path('service-job/', service_job, name='service-job'),
    path('service-job-status/', service_job_status, name='service-job-status'),
    path('service_booking/', service_booking, name="service_booking")
]   

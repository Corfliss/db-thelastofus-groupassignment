from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from django.core.exceptions import ValidationError

from django.contrib.auth.models import AbstractUser
from django.db import models

class Service(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting For Worker to Depart'),
        ('arrived', 'Arrived At Location'),
        ('working', 'Providing Service'),
        ('completed', 'Service Completed'),
        ('cancelled', 'Order Cancelled')
    ]

    subcategory_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100) # will become foreign key
    order_date = models.DateTimeField(auto_now_add=True)
    working_date = models.DateTimeField()
    session = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=7, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='others')

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):

    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('worker', 'Worker'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    
    # Attributes
    phone_number = models.CharField(
        max_length=15, unique=True,
        validators=[RegexValidator(regex=r'^\d{9,15}$', message="Phone number must be between 9 and 15 digits.")]
    )

    sex_choices = (
        ('male', 'Male'),
        ('female', 'Female'),
    )

    sex = models.CharField(max_length=6, choices=sex_choices)
    birthdate = models.DateField()
    address = models.TextField()
    email = None
    
    # Log in Attributes
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'sex', 'birthdate', 'address']

    class Meta:
        db_table = 'main_customuser' 

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='customer_profile')
    
    def clean(self):
        
        if self.user.user_type != 'customer':
            raise ValidationError("The user must be a customer.")

    def __str__(self):
        return f"Customer Profile of {self.user.username}"


class Worker(models.Model):
    BANK_CHOICES = [
        ('GoPay', 'GoPay'),
        ('OVO', 'OVO'),
        ('Virtual Account BCA', 'Virtual Account BCA'),
        ('Virtual Account BNI', 'Virtual Account BNI'),
        ('Virtual Account Mandiri', 'Virtual Account Mandiri'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='worker_profile')
    bank_name = models.CharField(max_length=30, choices=BANK_CHOICES, unique=True)

    account_number = models.CharField(
        max_length=12,
        unique=True,
        validators=[MinLengthValidator(9), MaxLengthValidator(12)]
    )

    npwp = models.CharField(  
        max_length=16,
        unique=True,
        validators=[MinLengthValidator(16), MaxLengthValidator(16)]
    )

    def clean(self):
        if self.user.user_type != 'worker':
            raise ValidationError("The user must be a worker.")

    def __str__(self):
        return f"Worker Profile of {self.user.username}"



# from django.core.validators import RegexValidator
from django.db import models
# import uuid

# class Service(models.Model):
#     STATUS_CHOICES = [
#         ('waiting', 'Waiting For Worker to Depart'),
#         ('arrived', 'Arrived At Location'),
#         ('working', 'Providing Service'),
#         ('completed', 'Service Completed'),
#         ('cancelled', 'Order Cancelled')
#     ]

#     subcategory_name = models.CharField(max_length=100)
#     username = models.CharField(max_length=100) # will become foreign key
#     order_date = models.DateTimeField(auto_now_add=True)
#     working_date = models.DateTimeField()
#     session = models.CharField(max_length=100)
#     total_amount = models.DecimalField(max_digits=7, decimal_places=2)
#     status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='others')

#     def __str__(self):
#         return self.subcategory_name

# class User(models.Model):
#     # Variable che for the attributes
#     sex_choices = (('male', 'Male'), ('female', 'Female'))
#     validators_phone=[RegexValidator(regex=r'^\d{9,15}$', message="Phone number must be between 9 and 15 digits.")]

#     # The attributes
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=255)
#     sex = models.CharField(max_length=6, choices=sex_choices)
#     phone_number = models.CharField(max_length=15, unique=True, validators=validators_phone)
#     password = models.CharField(max_length=255)
#     birthdate = models.DateField()
#     address = models.TextField()
#     mypay_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

#     # Log in Attributes
#     USERNAME_FIELD = 'phone_number'
#     REQUIRED_FIELDS = ['username', 'sex', 'birthdate', 'address']
    
#     def __str__(self):
#         return f"User: {self.name}"

# ##################################
# # The old CustomUser, deprecated #
# ##################################
# # class CustomUser(AbstractUser):
# #     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
# #     USER_TYPE_CHOICES = (
# #         ('customer', 'Customer'),
# #         ('worker', 'Worker'),
# #     )
    
# #     user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    
# #     # Attributes
# #     phone_number = models.CharField(
# #         max_length=15, unique=True,
# #         validators=[RegexValidator(regex=r'^\d{9,15}$', message="Phone number must be between 9 and 15 digits.")]
# #     )

# #     sex_choices = (
# #         ('male', 'Male'),
# #         ('female', 'Female'),
# #     )

# #     sex = models.CharField(max_length=6, choices=sex_choices)
# #     birthdate = models.DateField()
# #     address = models.TextField()
# #     email = None
    
# #     # Log in Attributes
# #     USERNAME_FIELD = 'phone_number'
# #     REQUIRED_FIELDS = ['username', 'sex', 'birthdate', 'address']

# #     class Meta:
# #         db_table = 'main_customuser' 

# #     def __str__(self):
# #         return f"{self.username} ({self.get_user_type_display()})"

# class Customer(User):
#     level = models.CharField(max_length=50, default="Standard")

#     def __str__(self):
#         return f"Customer: {self.name}"
    
# class Worker(User):
#     bank_name = models.CharField(max_length=100)
#     account_number = models.CharField(max_length=50, unique=True)
#     npwp = models.CharField(max_length=20, unique=True)
#     avatar_url = models.URLField()

#     # Set default to 0 for these attributes
#     rate = models.FloatField(default=0.0)
#     total_finish_order = models.IntegerField(default=0)

#     def __str__(self):
#         return f"Worker: {self.name}"
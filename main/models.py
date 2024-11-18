from django.db import models

# Create your models here.
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
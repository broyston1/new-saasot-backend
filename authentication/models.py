from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import CharField





class Company(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    
class CustomUser(AbstractUser):

    ADMIN = 1
    USER = 3
    STAFF = 2
    SUPERADMIN = 4
      
    ROLE_CHOICES = (
          (ADMIN, 'Admin'),
          (STAFF, 'User with staff input'),
          (USER, 'User with view only'),
          (SUPERADMIN, 'SUPERADMIN')
          
        )

    email_verified = models.BooleanField(default=False)
    forget_password_token = models.TextField(null=True, blank=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True)
    is_true = models.BooleanField(default=False)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, null=True, blank=True, related_name='company')


    def __str__(self):
        return self.email


from django.db import models

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from authentication.models import CustomUser, Company

class RevenueType(models.Model):
    months = models.IntegerField(default=0)
    updated_at = models.DateTimeField(null=False, blank=False, auto_now=True)
    revenue_type = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.revenue_type


class ProductServiceType(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='company_product_service_type')
    productp_service_type = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.productp_service_type
    

class ProductService(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
    product_name = models.CharField(max_length=300)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='company_product_service')
    productp_service_type = models.ForeignKey('ProductServiceType', on_delete=models.CASCADE, null=True)
    revenue_type = models.ForeignKey('RevenueType', on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)


class ExpectedMonths(models.Model):
    months = models.IntegerField(default=0)
    company = models.OneToOneField(Company, on_delete=models.CASCADE, null=False, blank=False, related_name='company_months')

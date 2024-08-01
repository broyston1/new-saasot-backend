from email.policy import default
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from authentication.models import CustomUser, Company
from services.models import ProductService
from django.contrib.postgres.fields import ArrayField, JSONField

# Create your models here.


class Transaction(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='company_transaction')
    transaction_id = models.IntegerField(null=True)
    customer_name = models.CharField(max_length=400)
    f_cst_name = models.CharField(max_length=400, null=True)
    transaction_name = models.CharField(max_length=100, null=True)
    order_close_data = models.DateField()
    billing_method = models.CharField(max_length=30)
    cancel_date = models.DateField(null=True, blank=True)
    invoice_number = models.IntegerField(blank=None, default=None)
    invoice_adresss = models.TextField(max_length=300, null=True)
    other_invoice_info = models.TextField(max_length=300, null=True)
    red_flag = models.BooleanField(default=False, null=True)
    is_active = models.BooleanField(default=False, null=True)  # Add this line

    def __str__(self):
        return str(self.id)


class Item(models.Model):

    class SUBSCRIPTIONSTATUS(models.TextChoices):
        ACTIVE = 'active', _('active')
        PENDING_RENEWAL = 'pending renewal', _('pending renewal')
        CANCELLED = 'cancelled', _('cancelled')

    item_description = models.TextField(max_length=200, null=True)
    quantity = models.IntegerField(default=0)
    s_start_d = models.DateTimeField(blank=True, null=True)
    s_end_d = models.DateTimeField(blank=True, null=True)
    subscription_status = models.CharField(max_length=200, null=True, blank=True, choices=SUBSCRIPTIONSTATUS.choices)
    subscription_terms_month = models.IntegerField(null=True, default=None)
    arr = models.FloatField(default=None, null=True)
    sale_price = models.FloatField(default=0)
    # other_metric1 =
    # other_metric2 =  
    cancel_date = models.DateTimeField(blank=True, null=True)
    total_revenue = models.FloatField()
    amount = models.FloatField(default=0)
    productp_service = models.ForeignKey(ProductService, on_delete=models.CASCADE, null=False , blank=False)
    tansaction = models.ForeignKey('Transaction', on_delete=models.CASCADE, null=False, blank=False, related_name='tansaction')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # return str(self.tansaction.customer_name)
        return str(self.id)

class Calculation(models.Model):

    items = models.OneToOneField('Item', on_delete=models.CASCADE, null=False, blank=False, related_name='items', default=None)
    revenue = ArrayField(models.JSONField(), blank=True)
    deffered_revenue = ArrayField(models.JSONField(), blank=True)
    billing = ArrayField(models.JSONField(), blank=True)
    arr =  ArrayField(models.JSONField(), blank=True, null=True)

    def __str__(self):
        return str(self.items.id)


class CalculationMonths(models.Model):

    items = models.OneToOneField('Item', on_delete=models.CASCADE, null=False, blank=False, related_name='item', default=None)
    revenue = ArrayField(models.JSONField(), blank=True)
    deffered_revenue = ArrayField(models.JSONField(), blank=True)
    billing = ArrayField(models.JSONField(), blank=True)
    arr =  ArrayField(models.JSONField(), blank=True, null=True)

    def __str__(self):
        return str(self.items)


class CloseDate(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
    close_date = models.DateTimeField(blank=True, null=True)
    close_period = models.BooleanField(default=True, null=False)
    # models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class ArrGracePeriod(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='company_grace_period')
    months = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)
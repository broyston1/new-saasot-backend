
import threading

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models.signals import Signal


from invoice.saasot_calculation.revenue1 import* 
from invoice.saasot_calculation import revenue_month
from  invoice.models import Calculation, Item, CalculationMonths
from .models import ProductService, RevenueType

# -----------------------signal for Calculation after update----------------------------------
@receiver(post_save, sender=ProductService)
def calculation_on_ProductService_save(sender, instance, created, **kwargs):
    # Your signal logic goes here
    if created:
        print("A new instance of MyModel has been created.")
    else:
        items = Item.objects.filter(productp_service = instance)
        for item in items:

# ---------------by day calling function-----------------------
            rev = revenue(item)
            bill = billing(item)
            # def_rev = deferred_revenue(item)

# -----------------------by month calling function---------------------
            rev_mth = revenue_month.revenue(item)
            bill_mth = revenue_month.billing(item)
            # def_rev_mth = revenue_month.deferred_revenue(item)

# -----------------------------by day updating or saving new calculations-----------------------------------
            try:
                calculation = Calculation.objects.get(items=item)
                if item.productp_service.revenue_type.revenue_type == "over life of subscription":
                    arr = item_arr(item)
                    calculation.revenue = rev
                    calculation.save()
                    calculation.billing = bill
                    def_rev = deferred_revenue(item)
                    calculation.deffered_revenue = def_rev
                    calculation.arr = arr
                    calculation.save()
                else:
                    calculation.revenue = rev
                    calculation.billing = bill
                    calculation.save()
                    def_rev = deferred_revenue(item)
                    calculation.deffered_revenue = def_rev
                    calculation.save()
            except:
                if item.productp_service.revenue_type.revenue_type == "over life of subscription":
                    arr = item_arr(item)
                    def_rev = deferred_revenue(item)
                    Calculation.objects.create(items=item, revenue=rev,
                    deffered_revenue=def_rev, billing=bill,
                    arr = arr
                    )
                else:
                    def_rev = deferred_revenue(item)
                    Calculation.objects.create(items=item, revenue=rev,
                    deffered_revenue=def_rev, billing=bill
                    )

# -----------------------------by momnth updating or saving new calculations-----------------------------------
            try:
                calculation = CalculationMonths.objects.get(items=item)
                if item.productp_service.revenue_type.revenue_type == "over life of subscription":
                    arr_mth = revenue_month.item_arr(item)
                    calculation.revenue = rev_mth
                    calculation.save()
                    def_rev_mth = revenue_month.deferred_revenue(item)
                    calculation.billing = bill_mth
                    calculation.deffered_revenue = def_rev_mth
                    calculation.arr = arr
                    calculation.save()
                else:
                    calculation.revenue = rev_mth
                    calculation.billing = bill_mth
                    calculation.save()
                    def_rev_mth = revenue_month.deferred_revenue(item)
                    calculation.deffered_revenue = def_rev_mth
                    calculation.save()
            except:
                if item.productp_service.revenue_type.revenue_type == "over life of subscription":
                    arr = item_arr(item)
                    def_rev_mth = revenue_month.deferred_revenue(item)
                    CalculationMonths.objects.create(items=item, revenue=rev_mth,
                    deffered_revenue=def_rev_mth, billing=bill_mth,
                    arr = arr_mth
                    )
                else:
                    def_rev_mth = revenue_month.deferred_revenue(item)
                    CalculationMonths.objects.create(items=item, revenue=rev_mth,
                    deffered_revenue=def_rev_mth, billing=bill_mth
                    )
        print("An instance of MyModel has been updated.")


calculation_on_expected_life = Signal()
@receiver(calculation_on_expected_life)
def calculation_on_expected_life_save(sender, instance, created, user, **kwargs):
    if created:
        print("A new instance of MyModel has been created.")
    else:
        items = Item.objects.filter(productp_service__revenue_type = instance, tansaction__user__company=user.company)
        for item in items:

# ---------------by day calling function-----------------------
            rev = revenue(item)
            bill = billing(item)
            # def_rev = deferred_revenue(item)

# -----------------------by month calling function---------------------
            rev_mth = revenue_month.revenue(item)
            bill_mth = revenue_month.billing(item)
            # def_rev_mth = revenue_month.deferred_revenue(item)

# -----------------------------by day updating or saving new calculations-----------------------------------
            try:
                calculation = Calculation.objects.get(items=item)
                if item.productp_service.revenue_type.revenue_type == "over life of subscription":
                    arr = item_arr(item)
                    calculation.revenue = rev
                    calculation.save()
                    calculation.billing = bill
                    def_rev = deferred_revenue(item)
                    calculation.deffered_revenue = def_rev
                    calculation.arr = arr
                    calculation.save()
                else:
                    calculation.revenue = rev
                    calculation.save()
                    def_rev = deferred_revenue(item)
                    calculation.billing = bill
                    calculation.deffered_revenue = def_rev
                    calculation.save()
            except:
                if item.productp_service.revenue_type.revenue_type == "over life of subscription":
                    arr = item_arr(item)
                    def_rev = deferred_revenue(item)
                    Calculation.objects.create(items=item, revenue=rev,
                    deffered_revenue=def_rev, billing=bill,
                    arr = arr
                    )
                else:
                    def_rev = deferred_revenue(item)
                    Calculation.objects.create(items=item, revenue=rev,
                    deffered_revenue=def_rev, billing=bill
                    )

# -----------------------------by momnth updating or saving new calculations-----------------------------------
            try:
                calculation = CalculationMonths.objects.get(items=item)
                if item.productp_service.revenue_type.revenue_type == "over life of subscription":
                    arr_mth = revenue_month.item_arr(item)
                    calculation.revenue = rev_mth
                    calculation.save()
                    def_rev_mth = revenue_month.deferred_revenue(item)
                    calculation.billing = bill_mth
                    calculation.deffered_revenue = def_rev_mth
                    calculation.arr = arr
                    calculation.save()
                else:
                    calculation.revenue = rev_mth
                    calculation.save()
                    def_rev_mth = revenue_month.deferred_revenue(item)
                    calculation.billing = bill_mth
                    calculation.deffered_revenue = def_rev_mth
                    calculation.save()
            except:
                if item.productp_service.revenue_type.revenue_type == "over life of subscription":
                    arr = item_arr(item)
                    def_rev_mth = revenue_month.deferred_revenue(item)
                    Calculation.objects.create(items=item, revenue=rev_mth,
                    deffered_revenue=def_rev_mth, billing=bill_mth,
                    arr = arr_mth
                    )
                else:
                    def_rev_mth = revenue_month.deferred_revenue(item)
                    Calculation.objects.create(items=item, revenue=rev_mth,
                    deffered_revenue=def_rev_mth, billing=bill_mth
                    )
        print("An instance of MyModel has been updated.")

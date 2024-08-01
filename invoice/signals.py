from configparser import MAX_INTERPOLATION_DEPTH
import threading
import calendar
from datetime import datetime

from django.dispatch import receiver
from django.db.models.signals import post_save
from dateutil.relativedelta import relativedelta
from django.db.models.signals import Signal

from .saasot_calculation.revenue1 import *
from .saasot_calculation import revenue_month
from .models import *

from .serializers import (TransactionScreenSerilizer)

# -----------------------signal for Calculation after update and create----------------------------------

@receiver(post_save, sender=Item)
def calculation_on_item_save(sender, instance, created, **kwargs):
    obj = instance

    # Functions to calculate revenue, billing, deferred revenue
    rev = revenue(obj)
    bill = billing(obj)
    def_rev = deferred_revenue(obj)
    rev_mth = revenue_month.revenue(obj)
    bill_mth = revenue_month.billing(obj)
    def_rev_mth = revenue_month.deferred_revenue(obj)

    if created:
        if obj.productp_service.revenue_type.revenue_type == "over life of subscription":
            arr = item_arr(obj)
            arr_mth = revenue_month.item_arr(obj)

            # Creating day calculation
            Calculation.objects.create(items=obj, revenue=rev,
                                       deffered_revenue=def_rev, billing=bill,
                                       arr=arr)

            # Creating month calculation
            CalculationMonths.objects.create(items=obj, revenue=rev_mth,
                                             deffered_revenue=def_rev_mth, billing=bill_mth,
                                             arr=arr_mth)
        else:
            # Creating day calculation
            Calculation.objects.create(items=obj, revenue=rev,
                                       deffered_revenue=def_rev, billing=bill)

            # Creating month calculation
            CalculationMonths.objects.create(items=obj, revenue=rev_mth,
                                             deffered_revenue=def_rev_mth, billing=bill_mth)
    else:
        try:
            calculation = Calculation.objects.get(items=obj)
            if obj.productp_service.revenue_type.revenue_type == "over life of subscription":
                arr = item_arr(obj)
                calculation.revenue = rev
                calculation.billing = bill
                calculation.deffered_revenue = def_rev
                calculation.arr = arr
            else:
                calculation.revenue = rev
                calculation.billing = bill
                calculation.deffered_revenue = def_rev
            calculation.save()
        except Calculation.DoesNotExist:
            if obj.productp_service.revenue_type.revenue_type == "over life of subscription":
                arr = item_arr(obj)
                Calculation.objects.create(items=obj, revenue=rev,
                                           deffered_revenue=def_rev, billing=bill,
                                           arr=arr)
            else:
                Calculation.objects.create(items=obj, revenue=rev,
                                           deffered_revenue=def_rev, billing=bill)

        try:
            calculation = CalculationMonths.objects.get(items=obj)
            if obj.productp_service.revenue_type.revenue_type == "over life of subscription":
                arr_mth = revenue_month.item_arr(obj)
                calculation.revenue = rev_mth
                calculation.billing = bill_mth
                calculation.deffered_revenue = def_rev_mth
                calculation.arr = arr_mth
            else:
                calculation.revenue = rev_mth
                calculation.billing = bill_mth
                calculation.deffered_revenue = def_rev_mth
            calculation.save()
        except CalculationMonths.DoesNotExist:
            if obj.productp_service.revenue_type.revenue_type == "over life of subscription":
                arr_mth = revenue_month.item_arr(obj)
                CalculationMonths.objects.create(items=obj, revenue=rev_mth,
                                                 deffered_revenue=def_rev_mth, billing=bill_mth,
                                                 arr=arr_mth)
            else:
                CalculationMonths.objects.create(items=obj, revenue=rev_mth,
                                                 deffered_revenue=def_rev_mth, billing=bill_mth)

        print("An instance of MyModel has been updated.")



# @receiver(post_save, sender=Item)
# def calculation_on_item_save(sender, instance, created, **kwargs):
#     # Your signal logic goes here
#     if created:
#         # print("A new instance of MyModel has been created calculation_on_item_save.")

#         # by day calling function
#         obj = instance
#         # print( 'calculation_on_item_save instance ', instance )

#         rev = revenue(obj)
#         bill = billing(obj)
#         def_rev = deferred_revenue(obj)

#         print('def_rev (((((((((((((((((())))))))))))))))))')
#         print(def_rev)

#         # by month calling function
#         rev_mth = revenue_month.revenue(obj)
#         bill_mth = revenue_month.billing(obj)
#         def_rev_mth = revenue_month.deferred_revenue(obj)

#         if obj.productp_service.revenue_type.revenue_type == "over life of subscription":
#             arr = item_arr(obj)

#             print( 'calculation_on_item_save ARR ', arr )

#             # print(arr, "{{{{{{{{{{{{{{{{{{}}}}}}}}}}}}}}}}}}")
#             arr_mth = revenue_month.item_arr(obj)

#             # by day creating object
#             Calculation.objects.create(items=obj, revenue=rev,
#                                        deffered_revenue=def_rev, billing=bill,
#                                        arr=arr
#                                        )
#             # print( 'Calculation ARR CREATED 1' )

#             Calculation.objects.create(items=obj, revenue=rev, deffered_revenue=def_rev, billing=bill, arr=arr)

#             # print( 'Calculation ARR CREATED 2' )

#             # by month creating object
#             CalculationMonths.objects.create(items=obj, revenue=rev_mth,
#                                              deffered_revenue=def_rev_mth, billing=bill_mth,
#                                              arr=arr_mth
#                                              )
        
#             # print( 'Calculation ARR CREATED 3' )

#         else:

            

#             Calculation.objects.create(items=obj, revenue=rev,
#                                        deffered_revenue=def_rev, billing=bill
#                                        )

#             # by month creating object
#             CalculationMonths.objects.create(items=obj, revenue=rev_mth,
#                                              deffered_revenue=def_rev_mth, billing=bill_mth
#                                              )
#             print('Else (((((((((((((((((( Success ))))))))))))))))))')
#     else:

        
#         print("PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP")
#         # by day calling function
#         obj = instance
#         rev = revenue(obj)
#         bill = billing(obj)
#         def_rev = deferred_revenue(obj)

# # -----------------------by month calling function---------------------
#         rev_mth = revenue_month.revenue(obj)
#         bill_mth = revenue_month.billing(obj)
#         def_rev_mth = revenue_month.deferred_revenue(obj)

#         try:

#             print("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")
#             calculation = Calculation.objects.get(items=obj)
#             if obj.productp_service.revenue_type.revenue_type == "over life of subscription":
#                 arr = item_arr(obj)
                
#                 calculation.revenue = rev
#                 calculation.billing = bill
#                 calculation.deffered_revenue = def_rev
#                 calculation.arr = arr
#                 calculation.save()
#             else:
#                 calculation.revenue = rev
#                 calculation.billing = bill
#                 calculation.deffered_revenue = def_rev
#                 calculation.save()
#         except:
#             print('sdfdsfdfsd gfdffddf dfsdfsfsfsfsf')
#             if obj.productp_service.revenue_type.revenue_type == "over life of subscription":
#                 arr = item_arr(obj)
#                 Calculation.objects.create(items=obj, revenue=rev,
#                                            deffered_revenue=def_rev, billing=bill,
#                                            arr=arr
#                                            )
#             else:
#                 Calculation.objects.create(items=obj, revenue=rev,
#                                            deffered_revenue=def_rev, billing=bill
#                                            )
# # -----------------------------by month-----------------------------------
#         try:
#             calculation = CalculationMonths.objects.get(items=obj)
#             if obj.productp_service.revenue_type.revenue_type == "over life of subscription":
#                 arr_mth = revenue_month.item_arr(obj)
#                 calculation.revenue = rev_mth
#                 calculation.billing = bill_mth
#                 calculation.deffered_revenue = def_rev_mth
#                 calculation.arr = arr_mth
#                 calculation.save()
#             else:
#                 calculation.revenue = rev_mth
#                 calculation.billing = bill_mth
#                 calculation.deffered_revenue = def_rev_mth
#                 calculation.save()
#         except:
#             if obj.productp_service.revenue_type.revenue_type == "over life of subscription":
#                 arr_mth = revenue_month.item_arr(obj)
#                 CalculationMonths.objects.create(items=obj, revenue=rev_mth,
#                                                  deffered_revenue=def_rev_mth, billing=bill_mth,
#                                                  arr=arr_mth
#                                                  )
#             else:
#                 CalculationMonths.objects.create(items=obj, revenue=rev_mth,
#                                                  deffered_revenue=def_rev_mth, billing=bill_mth
#                                                  )
#         print("An instance of MyModel has been updated.")


arr_grace_period_signal = Signal()

@receiver(arr_grace_period_signal)
def calculation_on_arr_grace_period_handler(sender, instance, created, user, **kwargs):
    # Your signal logic goes here
    print("A new instance of MyModel has been created.")
    threading.Thread(target=arr_grace, args=[user]).start()

import pytz
from collections import defaultdict
from datetime import datetime

from dateutil.relativedelta import relativedelta

from collections import defaultdict, OrderedDict
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Subquery, OuterRef, Count

def calculate_end_date(item, months_between, months_count):
    if months_count >= 1 and months_between > months_count:
        months_between = months_count

    if calendar.monthrange(item.s_end_d.year, item.s_end_d.month)[1] <= item.s_end_d.day:
        end_date = item.s_end_d + relativedelta(months=months_between, day=31)
    else:
        end_date = item.s_end_d + relativedelta(months=months_between)
    return end_date

def reset_item_calculation_before_grace(items):
    if items:
        for item in items:
            calc = Calculation.objects.get(items=item)
            arr = calc.arr
            new_arr = []
            
            # Check if arr is empty before accessing its last element
            if not arr:
                continue
            
            value = arr[-1]['value']
            start_date = item.s_start_d
            end_date = item.s_end_d

            current_date = start_date
            while current_date < end_date:
                if current_date.year == end_date.year and current_date.month == end_date.month:
                    if calendar.monthrange(current_date.year, current_date.month)[1] > end_date.day:
                        current_date += relativedelta(months=1)
                        break

                if current_date.day != start_date.day:
                    try:
                        current_date = current_date.replace(day=start_date.day)
                    except:
                        last_day_of_month = (current_date.replace(day=1) + relativedelta(months=1, days=-1)).day
                        current_date = current_date.replace(day=last_day_of_month)

                arr_dic = {
                    'date': current_date.strftime("%b %y"),
                    'update': False,
                    'value': value,
                    'pending_arr': current_date >= item.s_end_d
                }
                new_arr.append(arr_dic)
                current_date += relativedelta(months=1)
            calc.arr = new_arr
            calc.save()

def arr_grace(user):
    print('arr_grace running')

    grace_period = ArrGracePeriod.objects.filter(company=user.company).first()
    months_between = grace_period.months
    item_ids = Item.objects.filter(
        tansaction__user__company=user.company,
        productp_service__revenue_type__revenue_type="over life of subscription"
    ).values('tansaction_id')

    transactions = Transaction.objects.filter(id__in=item_ids).order_by('customer_name').distinct('customer_name')

    monthly_totals = defaultdict(lambda: defaultdict(float))

    for tsc in transactions:
        items = Item.objects.filter(
            tansaction__customer_name=tsc.customer_name,
            tansaction__user__company=user.company,
            productp_service__revenue_type__revenue_type="over life of subscription"
        ).order_by('-s_end_d')

        reset_item_calculation_before_grace(items)

        if items:
            for item in items:
                calc = Calculation.objects.get(items=item)
                for index, entry in enumerate(calc.arr):
                    date_str = entry['date']
                    date_obj = datetime.strptime(date_str, "%b %y")
                    formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                    value = entry['value']

                    if formatted_date not in monthly_totals[tsc.customer_name]:
                        monthly_totals[tsc.customer_name][formatted_date] = {'index': index, 'value': value, 't_id': item.tansaction_id, 'item_id': item.id}
                    else:
                        monthly_totals[tsc.customer_name][formatted_date]['value'] += value


    for customer_name, totals in monthly_totals.items():

        # Sorting the totals by date
        sorted_totals = sorted(totals.items(), key=lambda x: datetime.strptime(x[0], '%Y-%m-%d %H:%M:%S'))
        sorted_dates_values = [{'date': key, 'value': value['value'], 'index': value['index'], 't_id': value['t_id'], 'item_id': value['item_id']} for key, value in sorted_totals]

        missing_months = []
        if sorted_dates_values:
            first_date = datetime.strptime(sorted_dates_values[0]['date'], '%Y-%m-%d %H:%M:%S')
            last_date = datetime.strptime(sorted_dates_values[-1]['date'], '%Y-%m-%d %H:%M:%S')
            current_date = first_date

            while current_date < last_date:
                current_date += relativedelta(months=1)
                formatted_date = current_date.strftime("%Y-%m-%d %H:%M:%S")
                if formatted_date not in [entry['date'] for entry in sorted_dates_values]:
                    closest_entry = min(
                        sorted_dates_values, 
                        key=lambda x: abs(datetime.strptime(x['date'], '%Y-%m-%d %H:%M:%S') - current_date)
                    )
                    missing_months.append({
                        'date': formatted_date,
                        't_id': closest_entry['t_id'],
                        'item_id': closest_entry['item_id']
                    })

        missing_months = sorted(missing_months, key=lambda x: x['date'])

        if missing_months:
            before_after_transactions = []
            last_item_id = None
            for missing_month in missing_months:
                before_transaction = None
                after_transaction = None
                missing_month_date = datetime.strptime(missing_month['date'], '%Y-%m-%d %H:%M:%S')

                for entry in sorted_dates_values:
                    date = datetime.strptime(entry['date'], '%Y-%m-%d %H:%M:%S')
                    if date < missing_month_date:
                        before_transaction = entry
                    elif date > missing_month_date and after_transaction is None:
                        after_transaction = entry
                        break

                if before_transaction and after_transaction:
                    value_difference = after_transaction['value'] - before_transaction['value']
                    before_date = datetime.strptime(before_transaction['date'], '%Y-%m-%d %H:%M:%S')
                    after_date = datetime.strptime(after_transaction['date'], '%Y-%m-%d %H:%M:%S')
                    months_count = (after_date.year - before_date.year) * 12 + after_date.month - before_date.month - 1
                else:
                    value_difference = None
                    months_count = 0

                if last_item_id:
                    missing_month['item_id'] = last_item_id
                last_item_id = missing_month['item_id']

                before_after_transactions.append({
                    'missing_month': missing_month,
                    'before': before_transaction,
                    'after': after_transaction,
                    'value_difference': value_difference,
                    'months_count': months_count
                })

            for missing_item_transaction in before_after_transactions:
                months_count = missing_item_transaction['months_count']
                item_id = missing_item_transaction['missing_month']['item_id']
                try:
                    missing_item = Item.objects.get(id=item_id)
                except Item.DoesNotExist:
                    print(f"Item with id {item_id} does not exist.")
                    continue

                try:
                    calculate_arr(missing_item, months_between, months_count)
                    calculate_arr_by_month(missing_item, months_between, months_count)
                except Exception as e:
                    print(f"Error processing item with id {item_id}: {e}")

        else:
            # No missing months, print the last t_id and item_id
            if sorted_dates_values:
                last_entry = sorted_dates_values[-1]
                # print(f"Customer: {customer_name}, Last t_id: {last_entry['t_id']}, Last item_id: {last_entry['item_id']}")

                try:
                    item_id = last_entry['item_id']
                    item = Item.objects.get(id=item_id)
                    calculate_arr(item, months_between, 0)
                    calculate_arr_by_month(item, months_between, 0)
                except Exception as e:
                    print('Exception: ', e)


    # for customer_name, totals in monthly_totals.items():

    #     # if customer_name == 'Branford (CT) Fire Department, Town of':
    #     #     print('<><><><><><><><><><><>< 1. totals ><><><><><><><><><><><><>')
    #     #     print(totals)

    #     sorted_totals = sorted(totals.items(), key=lambda x: datetime.strptime(x[0], '%Y-%m-%d %H:%M:%S'))
    #     sorted_dates_values = [{'date': key, 'value': value['value'], 'index': value['index'], 't_id': value['t_id'], 'item_id': value['item_id']} for key, value in sorted_totals]

    #     missing_months = []
    #     if sorted_dates_values:
    #         first_date = datetime.strptime(sorted_dates_values[0]['date'], '%Y-%m-%d %H:%M:%S')
    #         last_date = datetime.strptime(sorted_dates_values[-1]['date'], '%Y-%m-%d %H:%M:%S')
    #         current_date = first_date

    #         while current_date < last_date:
    #             current_date += relativedelta(months=1)
    #             formatted_date = current_date.strftime("%Y-%m-%d %H:%M:%S")
    #             if formatted_date not in [entry['date'] for entry in sorted_dates_values]:
    #                 closest_entry = min(
    #                     sorted_dates_values, 
    #                     key=lambda x: abs(datetime.strptime(x['date'], '%Y-%m-%d %H:%M:%S') - current_date)
    #                 )
    #                 missing_months.append({
    #                     'date': formatted_date,
    #                     't_id': closest_entry['t_id'],
    #                     'item_id': closest_entry['item_id']
    #                 })

    #     missing_months = sorted(missing_months, key=lambda x: x['date'])

    #     if customer_name == 'Branford (CT) Fire Department, Town of' or customer_name == 'Ann Arbor Township (MI) Fire Department':
    #         print('<><><><><><><><><><><>< customer_name ><><><><><><><><><><><><>')
    #         print(missing_months)

    #     if missing_months:
    #         before_after_transactions = []
    #         last_item_id = None
    #         for missing_month in missing_months:
    #             before_transaction = None
    #             after_transaction = None
    #             missing_month_date = datetime.strptime(missing_month['date'], '%Y-%m-%d %H:%M:%S')

    #             for entry in sorted_dates_values:
    #                 date = datetime.strptime(entry['date'], '%Y-%m-%d %H:%M:%S')
    #                 if date < missing_month_date:
    #                     before_transaction = entry
    #                 elif date > missing_month_date and after_transaction is None:
    #                     after_transaction = entry
    #                     break

    #             if before_transaction and after_transaction:
    #                 value_difference = after_transaction['value'] - before_transaction['value']
    #                 before_date = datetime.strptime(before_transaction['date'], '%Y-%m-%d %H:%M:%S')
    #                 after_date = datetime.strptime(after_transaction['date'], '%Y-%m-%d %H:%M:%S')
    #                 months_count = (after_date.year - before_date.year) * 12 + after_date.month - before_date.month - 1
    #             else:
    #                 value_difference = None
    #                 months_count = 0

    #             if last_item_id:
    #                 missing_month['item_id'] = last_item_id
    #             last_item_id = missing_month['item_id']

    #             if customer_name == 'Branford (CT) Fire Department, Town of':
    #                 print('<<<<<<<<<<<<<<<<<<<< last_item_id >>>>>>>>>>>>>>>>>>>')
    #                 print(missing_month['t_id'])
    #                 print(missing_month['item_id'])

    #             before_after_transactions.append({
    #                 'missing_month': missing_month,
    #                 'before': before_transaction,
    #                 'after': after_transaction,
    #                 'value_difference': value_difference,
    #                 'months_count': months_count
    #             })

    #         for missing_item_transaction in before_after_transactions:
    #             months_count = missing_item_transaction['months_count']
    #             item_id = missing_item_transaction['missing_month']['item_id']
    #             try:
    #                 missing_item = Item.objects.get(id=item_id)
    #             except Item.DoesNotExist:
    #                 print(f"Item with id {item_id} does not exist.")
    #                 continue

    #             try:
    #                 calculate_arr(missing_item, months_between, months_count)
    #                 # calculate_arr_by_month(missing_item, months_between, months_count)
    #             except Exception as e:
    #                 print(f"Error processing item with id {item_id}: {e}")

    #     else:
    #         transactions = Transaction.objects.filter(id__in=item_ids, company_id=user.company) \
    #         .order_by('customer_name', '-pk')

    #         first_transaction_ids = OrderedDict()
    #         for tsc in transactions:
    #             customer_name = tsc.customer_name
    #             if customer_name not in first_transaction_ids:
    #                 first_transaction_ids[customer_name] = tsc.id

    #         for customer_name, transaction_id in first_transaction_ids.items():
    #             items = Item.objects.filter(
    #                 tansaction__customer_name=customer_name,
    #                 tansaction__user__company=user.company,
    #                 tansaction__id=transaction_id,
    #                 productp_service__revenue_type__revenue_type="over life of subscription"
    #             ).order_by('-pk')

    #             if items.exists():
    #                 max_end_date_item = items.first()
    #                 try:
    #                     if months_between > 0:
    #                         calculate_arr(max_end_date_item, months_between, 0)
    #                 except Exception as e:
    #                     print('Exception: ', e)

def calculate_arr(item, months_between, months_count):
    try:
        calc = Calculation.objects.get(items=item)
        arr = calc.arr
        new_arr = []
        value = arr[-1]['value']
        start_date = item.s_start_d
        end_date = calculate_end_date(item, months_between, months_count)

        current_date = start_date
        while current_date < end_date:
            if current_date.year == end_date.year and current_date.month == end_date.month:
                if calendar.monthrange(current_date.year, current_date.month)[1] > end_date.day:
                    current_date += relativedelta(months=1)
                    break

            if current_date.day != start_date.day:
                try:
                    current_date = current_date.replace(day=start_date.day)
                except:
                    last_day_of_month = (current_date.replace(day=1) + relativedelta(months=1, days=-1)).day
                    current_date = current_date.replace(day=last_day_of_month)

            arr_dic = {
                'date': current_date.strftime("%b %y"),
                'update': False,
                'value': value,
                'pending_arr': current_date >= item.s_end_d
            }
            new_arr.append(arr_dic)
            current_date += relativedelta(months=1)
        calc.arr = new_arr

        # print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        # print(calc.arr)
        calc.save()
    except Exception as e:
        print('Exception Calculate Arr: ', e)

def calculate_arr_by_month(item, months_between, months_count):
    try:
        calc = CalculationMonths.objects.get(items=item)
        arr = calc.arr
        new_arr = []
        value = arr[-1]['value']
        start_date = item.s_start_d
        end_date = calculate_end_date(item, months_between, months_count)

        current_date = start_date
        while current_date < end_date:
            if current_date.year == end_date.year and current_date.month == end_date.month:
                if calendar.monthrange(current_date.year, current_date.month)[1] > end_date.day:
                    current_date += relativedelta(months=1)
                    break

            if current_date.day != start_date.day:
                try:
                    current_date = current_date.replace(day=start_date.day)
                except:
                    last_day_of_month = (current_date.replace(day=1) + relativedelta(months=1, days=-1)).day
                    current_date = current_date.replace(day=last_day_of_month)

            arr_dic = {
                'date': current_date.strftime("%b %y"),
                'update': False,
                'value': value,
                'pending_arr': current_date >= item.s_end_d
            }
            new_arr.append(arr_dic)
            current_date += relativedelta(months=1)
        calc.arr = new_arr
        calc.save()
    except Exception as e:
        print('Exception Calculate Arr by Month: ', e)


# # working
# def arr_grace(user):

#     print('arr_grace running')
    
#     grace_period = ArrGracePeriod.objects.filter(company=user.company).first()
#     months_between = grace_period.months
#     item_ids = Item.objects.filter(
#         tansaction__user__company=user.company,
#         productp_service__revenue_type__revenue_type="over life of subscription"
#     ).values('tansaction_id')
    
#     transactions = Transaction.objects.filter(id__in=item_ids).order_by('customer_name').distinct('customer_name')

#     monthly_totals = defaultdict(float)
#     for tsc in transactions:

#         # print('transactions loop running')
#         # print(tsc.customer_name)

#         # if tsc.customer_name == 'Branford (CT) Fire Department, Town of':
#         items = Item.objects.filter(
#             tansaction__customer_name=tsc.customer_name,
#             tansaction__user__company=user.company,
#             productp_service__revenue_type__revenue_type="over life of subscription"
#         ).order_by('-s_end_d')

#         reset_item_calculation_before_grace(items)

#         if items:
#             for item in items:
#                 calc = Calculation.objects.get(items=item)
#                 for index, entry in enumerate(calc.arr):
#                     date_str = entry['date']
#                     date_obj = datetime.strptime(date_str, "%b %y")
#                     formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
#                     value = entry['value']
                    
#                     if formatted_date not in monthly_totals:
#                         monthly_totals[formatted_date] = {'index': index, 'value': value, 't_id': item.tansaction_id, 'item_id': item.id}
#                     else:
#                         monthly_totals[formatted_date]['value'] += value

#     sorted_totals = sorted(monthly_totals.items(), key=lambda x: datetime.strptime(x[0], '%Y-%m-%d %H:%M:%S'))
#     sorted_dates_values = [{'date': key, 'value': value['value'], 'index': value['index'], 't_id': value['t_id'], 'item_id': value['item_id']} for key, value in sorted_totals]

#     # print('=========== sorted_dates_values ==========')
#     # print(sorted_dates_values)


#     missing_months = []
#     if sorted_dates_values:
#         first_date = datetime.strptime(sorted_dates_values[0]['date'], '%Y-%m-%d %H:%M:%S')
#         last_date = datetime.strptime(sorted_dates_values[-1]['date'], '%Y-%m-%d %H:%M:%S')
#         current_date = first_date

#         print('=========== first_date and last_date ==========')
#         print(first_date, ' First date and last date ' ,last_date)

#         while current_date < last_date:
#             current_date += relativedelta(months=1)
#             formatted_date = current_date.strftime("%Y-%m-%d %H:%M:%S")
#             if formatted_date not in [entry['date'] for entry in sorted_dates_values]:
#                 # Find the closest t_id and item_id from existing entries
#                 closest_entry = min(
#                     sorted_dates_values, 
#                     key=lambda x: abs(datetime.strptime(x['date'], '%Y-%m-%d %H:%M:%S') - current_date)
#                 )
#                 # Add missing date with t_id and item_id from the closest entry
#                 missing_months.append({
#                     'date': formatted_date,
#                     't_id': closest_entry['t_id'],
#                     'item_id': closest_entry['item_id']
#                 })

#                 print('missing_months ==========')
#                 print(missing_months)

#     missing_months = sorted(missing_months, key=lambda x: x['date'])

#     print('missing_months ==========')
#     print(missing_months)

#     if missing_months:
#         before_after_transactions = []
#         last_item_id = None
#         for missing_month in missing_months:
#             before_transaction = None
#             after_transaction = None
#             missing_month_date = datetime.strptime(missing_month['date'], '%Y-%m-%d %H:%M:%S')

#             for entry in sorted_dates_values:
#                 date = datetime.strptime(entry['date'], '%Y-%m-%d %H:%M:%S')
#                 if date < missing_month_date:
#                     before_transaction = entry
#                 elif date > missing_month_date and after_transaction is None:
#                     after_transaction = entry
#                     break

#             if before_transaction and after_transaction:
#                 value_difference = after_transaction['value'] - before_transaction['value']
#                 before_date = datetime.strptime(before_transaction['date'], '%Y-%m-%d %H:%M:%S')
#                 after_date = datetime.strptime(after_transaction['date'], '%Y-%m-%d %H:%M:%S')
#                 months_count = (after_date.year - before_date.year) * 12 + after_date.month - before_date.month - 1
#             else:
#                 value_difference = None
#                 months_count = 0

#             if last_item_id:
#                 missing_month['item_id'] = last_item_id
#             last_item_id = missing_month['item_id']

#             before_after_transactions.append({
#                 'missing_month': missing_month,
#                 'before': before_transaction,
#                 'after': after_transaction,
#                 'value_difference': value_difference,
#                 'months_count': months_count
#             })

#         for missing_item_transaction in before_after_transactions:
#             months_count = missing_item_transaction['months_count']
#             item_id = missing_item_transaction['missing_month']['item_id']
#             try:
#                 missing_item = Item.objects.get(id=item_id)
#             except Item.DoesNotExist:
#                 print(f"Item with id {item_id} does not exist.")
#                 continue
            
#             # Perform the calculations
#             try:
#                 calculate_arr(missing_item, months_between, months_count)
#                 calculate_arr_by_month(missing_item, months_between, months_count)
#             except Exception as e:
#                 print(f"Error processing item with id {item_id}: {e}")
        
#     else:
#         print('Else')

#         transactions = Transaction.objects.filter(id__in=item_ids, company_id=user.company) \
#         .order_by('customer_name', '-pk')
        
#         # print('transactions ================ ')
#         # print(transactions)

#         # Dictionary to store the first transaction ID for each customer_name
#         first_transaction_ids = OrderedDict()

#         # Iterate through the transactions and store the first occurrence for each customer_name
#         for tsc in transactions:
#             customer_name = tsc.customer_name
#             if customer_name not in first_transaction_ids:
#                 first_transaction_ids[customer_name] = tsc.id

#         # print('first_transaction_ids ================ ')
#         # print(first_transaction_ids)

#         for customer_name, transaction_id in first_transaction_ids.items():
#             # print(f"Customer Name: {customer_name}, Transaction ID: {transaction_id}")

#             items = Item.objects.filter(
#                 tansaction__customer_name=customer_name,
#                 tansaction__user__company=user.company,
#                 tansaction__id=transaction_id,  # Adding the transaction_id condition
#                 productp_service__revenue_type__revenue_type="over life of subscription"
#             ).order_by('-pk')

#             if items.exists():
#                 max_end_date_item = items.first()  # Get the first record from the ordered list

#                 # print('<<<<<<<<<<<<<<<< max_end_date_item >>>>>>>>>>>>>>>>')
#                 # print(max_end_date_item, ' max item id and grace period ', months_between)
#                 try:
#                     if months_between > 0:
#                         calculate_arr(max_end_date_item, months_between, 0)
#                         # calculate_arr_by_month(max_end_date_item, months_between, 0)
#                 except Exception as e:
#                     print('Exception: ', e)

#                 # print(f"Max End Date Item ID: {max_end_date_item.id}")


# 20 May code
# def arr_grace(user):
#     print('arr_grace running')

#     grace_period = ArrGracePeriod.objects.filter(company=user.company).first()
#     months_between = grace_period.months

#     item_ids = Item.objects.filter(
#         tansaction__user__company=user.company,
#         productp_service__revenue_type__revenue_type="over life of subscription"
#     ).values_list('tansaction_id', flat=True)

#     transactions = Transaction.objects.filter(id__in=item_ids).order_by('customer_name').distinct('customer_name')

#     customer_monthly_totals = defaultdict(lambda: defaultdict(float))

#     # Prefetch all necessary items and calculations in one go
#     items = Item.objects.filter(
#         tansaction__user__company=user.company,
#         productp_service__revenue_type__revenue_type="over life of subscription"
#     ).select_related('tansaction', 'productp_service').order_by('-s_end_d')

#     calculations = Calculation.objects.filter(items__in=items).select_related('items')

#     reset_item_calculation_before_grace(items)

#     items_by_customer = defaultdict(list)
#     for item in items:
#         items_by_customer[item.tansaction.customer_name].append(item)

#     calculations_by_item = defaultdict(list)
#     for calc in calculations:
#         calculations_by_item[calc.items.id].append(calc)

#     for customer_name, items in items_by_customer.items():
#         # reset_item_calculation_before_grace(items)

#         for item in items:
#             if item.id in calculations_by_item:
#                 calc = calculations_by_item[item.id][0]
#                 for index, entry in enumerate(calc.arr):
#                     date_str = entry['date']
#                     date_obj = datetime.strptime(date_str, "%b %y")
#                     formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
#                     value = entry['value']

#                     if formatted_date not in customer_monthly_totals[customer_name]:
#                         customer_monthly_totals[customer_name][formatted_date] = {'index': index, 'value': value, 't_id': item.tansaction_id, 'item_id': item.id}
#                     else:
#                         customer_monthly_totals[customer_name][formatted_date]['value'] += value

#     for customer_name, monthly_totals in customer_monthly_totals.items():
#         sorted_totals = sorted(monthly_totals.items(), key=lambda x: datetime.strptime(x[0], '%Y-%m-%d %H:%M:%S'))
#         sorted_dates_values = [{'date': key, 'value': value['value'], 'index': value['index'], 't_id': value['t_id'], 'item_id': value['item_id']} for key, value in sorted_totals]

#         # print(f"Customer: {customer_name}, Sorted dates and values: {sorted_dates_values}")

#         missing_months = []
#         if sorted_dates_values:
#             first_date = datetime.strptime(sorted_dates_values[0]['date'], '%Y-%m-%d %H:%M:%S')
#             last_date = datetime.strptime(sorted_dates_values[-1]['date'], '%Y-%m-%d %H:%M:%S')
#             current_date = first_date

#             print(f"Customer: {customer_name}, First date and last date: {first_date}, {last_date}")

#             while current_date < last_date:
#                 current_date += relativedelta(months=1)
#                 formatted_date = current_date.strftime("%Y-%m-%d %H:%M:%S")
#                 if formatted_date not in [entry['date'] for entry in sorted_dates_values]:
#                     closest_entry = min(
#                         sorted_dates_values, 
#                         key=lambda x: abs(datetime.strptime(x['date'], '%Y-%m-%d %H:%M:%S') - current_date)
#                     )
#                     missing_months.append({
#                         'date': formatted_date,
#                         't_id': closest_entry['t_id'],
#                         'item_id': closest_entry['item_id']
#                     })

#                     # print(f"Customer: {customer_name}, Missing month added: {missing_months[-1]}")

#         missing_months = sorted(missing_months, key=lambda x: x['date'])

#         if customer_name == 'Branford (CT) Fire Department, Town of':
#             print(f"Customer: {customer_name}, missing_months: {missing_months}")

#         if missing_months:
#             before_after_transactions = []
#             last_item_id = None
#             for missing_month in missing_months:
#                 before_transaction = None
#                 after_transaction = None
#                 missing_month_date = datetime.strptime(missing_month['date'], '%Y-%m-%d %H:%M:%S')

#                 for entry in sorted_dates_values:
#                     date = datetime.strptime(entry['date'], '%Y-%m-%d %H:%M:%S')
#                     if date < missing_month_date:
#                         before_transaction = entry
#                     elif date > missing_month_date and after_transaction is None:
#                         after_transaction = entry
#                         break

#                 if before_transaction and after_transaction:
#                     value_difference = after_transaction['value'] - before_transaction['value']
#                     before_date = datetime.strptime(before_transaction['date'], '%Y-%m-%d %H:%M:%S')
#                     after_date = datetime.strptime(after_transaction['date'], '%Y-%m-%d %H:%M:%S')
#                     months_count = (after_date.year - before_date.year) * 12 + after_date.month - before_date.month - 1
#                 else:
#                     value_difference = None
#                     months_count = 0

#                 if last_item_id:
#                     missing_month['item_id'] = last_item_id
#                 last_item_id = missing_month['item_id']

#                 before_after_transactions.append({
#                     'missing_month': missing_month,
#                     'before': before_transaction,
#                     'after': after_transaction,
#                     'value_difference': value_difference,
#                     'months_count': months_count
#                 })

#             for missing_item_transaction in before_after_transactions:
#                 months_count = missing_item_transaction['months_count']
#                 item_id = missing_item_transaction['missing_month']['item_id']
#                 try:
#                     missing_item = Item.objects.get(id=item_id)
#                 except Item.DoesNotExist:
#                     print(f"Item with id {item_id} does not exist.")
#                     continue
                
#                 try:
#                     calculate_arr(missing_item, months_between, months_count)
#                     calculate_arr_by_month(missing_item, months_between, months_count)
#                 except Exception as e:
#                     print(f"Error processing item with id {item_id}: {e}")
            
#         else:
#             # print(f"Customer: {customer_name}, No missing months, processing remaining transactions")

#             transactions = Transaction.objects.filter(id__in=item_ids, company_id=user.company).order_by('customer_name', '-pk')

#             first_transaction_ids = OrderedDict()

#             for tsc in transactions:
#                 customer_name = tsc.customer_name
#                 if customer_name not in first_transaction_ids:
#                     first_transaction_ids[customer_name] = tsc.id

#             for customer_name, transaction_id in first_transaction_ids.items():
#                 # print(f"Customer Name: {customer_name}, Transaction ID: {transaction_id}")

#                 items = Item.objects.filter(
#                     tansaction__customer_name=customer_name,
#                     tansaction__user__company=user.company,
#                     tansaction__id=transaction_id,
#                     productp_service__revenue_type__revenue_type="over life of subscription"
#                 ).order_by('-pk')

#                 if items.exists():
#                     max_end_date_item = items.first()

#                     # print(f"Max End Date Item ID: {max_end_date_item.id}, Grace period: {months_between}")
#                     try:
#                         if months_between > 0:
#                             calculate_arr(max_end_date_item, months_between, 0)
#                             calculate_arr_by_month(max_end_date_item, months_between, 0)
#                     except Exception as e:
#                         print(f"Exception processing item ID {max_end_date_item.id}: {e}")

#                     # print(f"Max End Date Item ID: {max_end_date_item.id}")
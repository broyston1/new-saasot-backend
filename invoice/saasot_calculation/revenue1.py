import calendar
from pickle import TRUE
from typing import final

from invoice.models import Transaction, Item, Calculation, CloseDate
from services.models import ExpectedMonths
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from dateutil import parser


def parse_date(date_str):
    # Parse the date string and return a datetime object
    date_obj = datetime.strptime(date_str, "%b %y")
    return date_obj


def revenue(obj):
    revenue_list_by_month = []

    # ---------------------revenue according to over life of subscription---------------------------
    if obj.productp_service.revenue_type.revenue_type == "over life of subscription":
        start_date = str(obj.s_start_d)
        end_date = str(obj.s_end_d)
        start_date = parser.parse(start_date).date()
        end_date = parser.parse(end_date).date()
        delta = end_date - start_date

        # get total days in subscription
        days = delta.days + 1

        # if end date is smaller than start assigning start_date month days
        if start_date >= end_date:
            days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]
            days = days_in_month * 1
        if days == 0:
            return revenue_list_by_month
        revenue_calc = obj.total_revenue / days

        # iterate start_date to end_date to assign value to each month
        if parser.parse(str(obj.tansaction.order_close_data)).date() < start_date:
            current_date = parser.parse(str(obj.tansaction.order_close_data)).date()
            while current_date < start_date + relativedelta(days=1):
                revenue = {}
                revenue['date'] = current_date.strftime("%b %y")
                revenue['value'] = 0
                revenue['update'] = False
                revenue_list_by_month.append(revenue)
                current_date += relativedelta(months=1)

        new_end_date = end_date
        if end_date.day != calendar.monthrange(end_date.year, end_date.month)[1]:
            new_end_date = end_date + relativedelta(days=1)

        incre = 1
        current_date = start_date
        if new_end_date < parser.parse(str(obj.tansaction.order_close_data)).date():
            new_end_date = parser.parse(str(obj.tansaction.order_close_data)).date()

        while current_date <= new_end_date or (new_end_date.month == current_date.month and new_end_date.year == current_date.year):
            revenue = {}

            if len(revenue_list_by_month) > 0:
                if incre == 1 and revenue_list_by_month[len(revenue_list_by_month) - 1]['date'] == current_date.strftime("%b %y"):
                    revenue_list_by_month.pop(len(revenue_list_by_month) - 1)

            if current_date == start_date:
                days_in_month = calendar.monthrange(current_date.year, current_date.month)[1] - current_date.day + 1
            elif end_date.month == current_date.month and end_date.year == current_date.year:
                days_in_month = end_date.day
            else:
                days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]
            revenue['date'] = current_date.strftime("%b %y")
            revenue['value'] = revenue_calc * days_in_month
            if current_date > end_date and (current_date.year - end_date.year) * 12 + current_date.month - end_date.month > 0:
                revenue['value'] = 0
            revenue['update'] = False
            revenue_list_by_month.append(revenue)
            current_date += relativedelta(months=1)
            incre += 1
        return revenue_list_by_month

    # ---------------------revenue according to immediately upon invoicing---------------------------
    elif obj.productp_service.revenue_type.revenue_type == "immediately upon invoicing":
        revenue = {}
        date = obj.tansaction.order_close_data
        revenue['date'] = date.strftime("%b %y")
        revenue['value'] = obj.total_revenue
        revenue['update'] = False
        revenue_list_by_month.append(revenue)
        return revenue_list_by_month

    # ---------------------revenue according to over the expected life of the customer---------------------------
    elif obj.productp_service.revenue_type.revenue_type == "over the expected life of the customer":
        if obj.created_at > obj.productp_service.revenue_type.updated_at:
            start_date = str(obj.tansaction.order_close_data)
            start_date = parser.parse(start_date).date()
            try:
                mth = ExpectedMonths.objects.get(company=obj.tansaction.user.company)
                mth = mth.months
            except Exception as e:
                mth = 0
            end_date = start_date + relativedelta(months=mth)
            delta = end_date - start_date
            days = delta.days
            if days == 0:
                return revenue_list_by_month
            revenue_calc = obj.total_revenue / days
            current_date = start_date
            while current_date <= end_date + relativedelta(days=1) or (end_date.month == current_date.month and end_date.year == current_date.year):
                revenue = {}

                if current_date == start_date:
                    days_in_month = calendar.monthrange(current_date.year, current_date.month)[1] - current_date.day + 1
                elif end_date.month == current_date.month and end_date.year == current_date.year:
                    days_in_month = end_date.day - 1
                else:
                    days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]

                revenue['date'] = current_date.strftime("%b %y")
                revenue['value'] = revenue_calc * days_in_month
                revenue['update'] = False
                revenue_list_by_month.append(revenue)
                current_date += relativedelta(months=1)
            return revenue_list_by_month
        else:
            close_date = CloseDate.objects.all().first()
            close_date = parser.parse(str(close_date.close_date)).date()
            start_date = str(obj.tansaction.order_close_data)
            start_date = parser.parse(start_date).date()
            try:
                mth = ExpectedMonths.objects.get(company=obj.tansaction.user.company)
                mth = mth.months
            except:
                mth = 0
            end_date = start_date + relativedelta(months=mth)
            new_date = start_date
            rp = 0
            days_in_sub = 0
            revenue_calc_ex = 0
            if start_date > close_date:
                calc = Calculation.objects.get(items=obj)
                revenue_calc = calc.revenue
                delta = relativedelta(close_date, start_date)
                fixed_months = delta.years * 12 + delta.months + 1
                current_date = start_date
                d = 0
                fixed_value = 0
                while current_date <= end_date + relativedelta(days=1) or (end_date.month == current_date.month and end_date.year == current_date.year):
                    revenue = {}
                    if d < fixed_months:
                        try:
                            revenue_list_by_month.append(revenue_calc[d])
                            fixed_value += revenue_calc[d]['value']
                        except:
                            revenue['date'] = current_date.strftime("%b %y")
                            revenue['value'] = 0
                            revenue['update'] = False
                            revenue_list_by_month.append(revenue)
                        current_date += relativedelta(months=1)
                        new_date = current_date
                        d += 1
                    else:
                        revenue = {}
                        if rp < 1:
                            delta = end_date - new_date
                            days_in_sub = delta.days + 1
                            if days_in_sub == 0:
                                return revenue_list_by_month
                            revenue_calc_ex = (obj.total_revenue - fixed_value) / days_in_sub

                        if current_date == start_date:
                            days_in_month = calendar.monthrange(current_date.year, current_date.month)[1] - current_date.day + 1
                        elif end_date.month == current_date.month and end_date.year == current_date.year:
                            days_in_month = end_date.day
                        else:
                            days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]

                        revenue['date'] = current_date.strftime("%b %y")
                        revenue['value'] = revenue_calc_ex * days_in_month
                        revenue['update'] = False
                        revenue_list_by_month.append(revenue)
                        current_date += relativedelta(months=1)
                        rp += 1
                return revenue_list_by_month

            else:
                start_date = str(obj.tansaction.order_close_data)
                start_date = parser.parse(start_date).date()
                try:
                    mth = ExpectedMonths.objects.get(company=obj.tansaction.user.company)
                    mth = mth.months
                except:
                    mth = 0
                end_date = start_date + relativedelta(months=mth)
                delta = end_date - start_date
                days = delta.days + 1
                if days == 0:
                    return revenue_list_by_month
                revenue_calc = obj.total_revenue / days

                current_date = start_date
                while current_date <= end_date + relativedelta(days=1) or (end_date.month == current_date.month and end_date.year == current_date.year):
                    revenue = {}

                    if current_date == start_date:
                        days_in_month = calendar.monthrange(current_date.year, current_date.month)[1] - current_date.day + 1
                    elif end_date.month == current_date.month and end_date.year == current_date.year:
                        days_in_month = end_date.day
                    else:
                        days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]

                    revenue['date'] = current_date.strftime("%b %y")
                    revenue['value'] = revenue_calc * days_in_month
                    revenue['update'] = False
                    revenue_list_by_month.append(revenue)
                    current_date += relativedelta(months=1)
                return revenue_list_by_month

    elif obj.productp_service.revenue_type.revenue_type == "Manual revenue recognition":
        return []



def billing(obj):
    date = ""
    revenue_list_by_month = []
    revenue = {}
    # date = Item.objects.exclude(s_start_d=None, tansaction=obj.tansaction).order_by('s_start_d').first().s_start_d
    # if date == None:
    date = obj.tansaction.order_close_data
    revenue['date'] = date.strftime("%b %y")
    revenue['value'] = obj.amount
    revenue_list_by_month.append(revenue)
    # revenue[date.strftime("%B %Y")]=abs(obj.total_revenue)
    return revenue_list_by_month



def deferred_revenue(obj):
    try:
        cal = Calculation.objects.get(items=obj)
        rev = cal.revenue
    except:
        rev = revenue(obj)
    revenue_list_by_month = []

    if obj.productp_service.revenue_type.revenue_type == "over life of subscription":
        start_date = str(obj.s_start_d)
        end_date = str(obj.s_end_d)
        start_date = parser.parse(start_date).date()
        end_date = parser.parse(end_date).date()
        delta = end_date - start_date
        days = delta.days + 1
        value = obj.total_revenue

        if start_date >= end_date:
            days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]
            days = days_in_month * 1
        revenue_calc = obj.total_revenue / days

        d = 0
        incre = 1

        if parser.parse(str(obj.tansaction.order_close_data)).date() < start_date:
            current_date = parser.parse(str(obj.tansaction.order_close_data)).date()
            while current_date < start_date + relativedelta(days=1):
                revenue1 = {}
                revenue1['date'] = current_date.strftime("%b %y")
                revenue1['value'] = obj.total_revenue
                revenue_list_by_month.append(revenue1)
                current_date += relativedelta(months=1)
                d += 1

        new_end_date = end_date
        if end_date.day != calendar.monthrange(end_date.year, end_date.month)[1]:
            new_end_date = end_date + relativedelta(days=1)

        current_date = start_date
        negative_value = 0
        if new_end_date < parser.parse(str(obj.tansaction.order_close_data)).date():
            new_end_date = parser.parse(str(obj.tansaction.order_close_data)).date()
        
        while current_date <= new_end_date or (new_end_date.month == current_date.month and new_end_date.year == current_date.year):
            revenue1 = {}

            if len(revenue_list_by_month) > 0 and incre == 1 and revenue_list_by_month[-1]['date'] == current_date.strftime("%b %y"):
                revenue_list_by_month.pop()
                d -= 1

            if d < len(rev):
                if parser.parse(str(obj.tansaction.order_close_data)).date() > current_date and (
                        current_date.month != parser.parse(str(obj.tansaction.order_close_data)).date().month or
                        current_date.year != parser.parse(str(obj.tansaction.order_close_data)).date().year):
                    negative_value -= rev[d]['value']
                    revenue1['value'] = negative_value
                    value -= rev[d]['value']
                else:
                    value -= rev[d]['value']
                    revenue1['value'] = value
                    if new_end_date.month == current_date.month and new_end_date.year == current_date.year and (new_end_date.year - end_date.year) * 12 + new_end_date.month - end_date.month > 0:
                        revenue1['value'] = negative_value + obj.total_revenue
            else:
                # handle the case when d exceeds the length of rev
                revenue1['value'] = value

            days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]
            revenue1['date'] = current_date.strftime("%b %y")
            revenue_list_by_month.append(revenue1)
            current_date += relativedelta(months=1)
            d += 1
            incre += 1

        return revenue_list_by_month

    elif obj.productp_service.revenue_type.revenue_type == "immediately upon invoicing":
        revenue1 = {}
        start_date = obj.tansaction.order_close_data
        end_date = start_date + relativedelta(months=48)
        current_date = start_date
        while current_date <= end_date + relativedelta(days=1) or (end_date.month == current_date.month and end_date.year == current_date.year):
            revenue1 = {}
            days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]
            revenue1['date'] = current_date.strftime("%b %y")
            revenue1['value'] = obj.amount - obj.total_revenue
            revenue_list_by_month.append(revenue1)
            current_date += relativedelta(months=1)
        return revenue_list_by_month

    elif obj.productp_service.revenue_type.revenue_type == "over the expected life of the customer":
        if obj.created_at > obj.productp_service.revenue_type.updated_at:
            start_date = str(obj.tansaction.order_close_data)
            start_date = parser.parse(start_date).date()
            try:
                mth = ExpectedMonths.objects.get(company=obj.tansaction.user.company)
                mth = mth.months
            except:
                mth = 0
            end_date = start_date + relativedelta(months=mth)
            delta = end_date - start_date
            days = delta.days + 1
            revenue_calc = obj.total_revenue / days
            value = obj.total_revenue

            current_date = start_date
            d = 0
            while current_date <= end_date + relativedelta(days=1) or (end_date.month == current_date.month and end_date.year == current_date.year):
                revenue1 = {}
                days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]
                if d < len(rev):
                    value -= rev[d]['value']
                revenue1['value'] = value
                revenue1['date'] = current_date.strftime("%b %y")
                revenue_list_by_month.append(revenue1)
                current_date += relativedelta(months=1)
                d += 1
            return revenue_list_by_month
        else:
            # ... (rest of the code)
            pass

    elif obj.productp_service.revenue_type.revenue_type == "Manual revenue recognition":
        return []




# def deferred_revenue(obj):
#     try:
#         cal = Calculation.objects.get(items=obj)
#         rev = cal.revenue
#     except:
#         rev = revenue(obj)
#     revenue_list_by_month = []

# # ---------------------deferred_revenue according to over life of subscription---------------------------
#     if obj.productp_service.revenue_type.revenue_type == "over life of subscription":
#         start_date = str(obj.s_start_d)
#         end_date = str(obj.s_end_d)
#         start_date = parser.parse(start_date).date()
#         end_date = parser.parse(end_date).date()
#         delta = end_date - start_date
#         days = delta.days+1
#         value = obj.total_revenue

#         if start_date >= end_date:
#             days_in_month = calendar.monthrange(
#                 start_date.year, start_date.month)[1]
#             days = days_in_month*1
#         revenue_calc = obj.total_revenue/days

#         d = 0
#         incre = 1

#         # if parser.parse(str(obj.tansaction.order_close_data)).date() > start_date:
#         #     current_date = start_date
#         #     negative_value = 0
#         #     # while current_date < start_date + relativedelta(days=1) and (start_date.month > current_date.month and start_date.year >= current_date.year):
#         #     while current_date < parser.parse(str(obj.tansaction.order_close_data)).date() + relativedelta(days=1) and current_date.month != parser.parse(str(obj.tansaction.order_close_data)).date().month:
#         #         revenue1 = {}
#         #         revenue1['date'] = current_date.strftime("%b %y")
#         #         negative_value -= rev[d]['value']
#         #         value -= rev[d]['value']
#         #         revenue1['value'] = negative_value
#         #         revenue_list_by_month.append(revenue1)
#         #         current_date += relativedelta(months=1)
#         #         d += 1

#         if parser.parse(str(obj.tansaction.order_close_data)).date() < start_date:
#             current_date = parser.parse(
#                 str(obj.tansaction.order_close_data)).date()
#             # while current_date < start_date + relativedelta(days=1) and (start_date.month > current_date.month and start_date.year >= current_date.year):
#             while current_date < start_date + relativedelta(days=1):
#                 revenue1 = {}
#                 revenue1['date'] = current_date.strftime("%b %y")
#                 revenue1['value'] = obj.total_revenue
#                 revenue_list_by_month.append(revenue1)
#                 current_date += relativedelta(months=1)
#                 d += 1

#         new_end_date = end_date
#         if end_date.day != calendar.monthrange(end_date.year, end_date.month)[1]:
#             new_end_date = end_date + relativedelta(days=1)

#         # print(d, "lennnnnnnnnnnnnnn", len(rev), "sasasa", parser.parse(str(obj.tansaction.order_close_data)).date(), "dateeeeeeeeeee", start_date)
#         current_date = start_date
#         negative_value = 0
#         if new_end_date < parser.parse(str(obj.tansaction.order_close_data)).date():
#             new_end_date = parser.parse(str(obj.tansaction.order_close_data)).date()
#         while current_date <= new_end_date or (new_end_date.month == current_date.month and new_end_date.year == current_date.year):
#             revenue1 = {}

#             if len(revenue_list_by_month) > 0:
#                 if incre == 1 and revenue_list_by_month[len(revenue_list_by_month)-1]['date'] == current_date.strftime("%b %y"):
#                     revenue_list_by_month.pop(len(revenue_list_by_month)-1)
#                     d = d-1

#             if (parser.parse(str(obj.tansaction.order_close_data)).date() > current_date and
#                  (current_date.month != parser.parse(str(obj.tansaction.order_close_data)).date().month or
#                  current_date.year != parser.parse(str(obj.tansaction.order_close_data)).date().year)
#                 ):
#                 negative_value -= rev[d]['value']
#                 revenue1['value'] = negative_value
#                 value -= rev[d]['value']
#             else:
#                 value -= rev[d]['value']    
#                 revenue1['value'] = value
#                 if new_end_date.month == current_date.month and new_end_date.year == current_date.year and (new_end_date.year - end_date.year) * 12 + new_end_date.month - end_date.month  > 0:
#                     revenue1['value'] = negative_value + obj.total_revenue

#             # date.append(current_date.strftime("%B %Y"))
#             days_in_month = calendar.monthrange(
#                 current_date.year, current_date.month)[1]
#             revenue1['date'] = current_date.strftime("%b %y")
#             revenue_list_by_month.append(revenue1)
#             current_date += relativedelta(months=1)
#             d += 1
#             incre += 1
#         return revenue_list_by_month

# # ---------------------deferred_revenue according to immediately upon invoicing---------------------------
#     elif obj.productp_service.revenue_type.revenue_type == "immediately upon invoicing":
#         revenue1 = {}
#         start_date = obj.tansaction.order_close_data
#         end_date = start_date+relativedelta(months=48)
#         current_date = start_date
#         while current_date <= end_date + relativedelta(days=1) or (end_date.month == current_date.month and end_date.year == current_date.year):
#             revenue1 = {}
#             days_in_month = calendar.monthrange(
#                 current_date.year, current_date.month)[1]
#             revenue1['date'] = current_date.strftime("%b %y")
#             revenue1['value'] = obj.amount-obj.total_revenue
#             revenue_list_by_month.append(revenue1)
#             current_date += relativedelta(months=1)
#         return revenue_list_by_month

# # ---------------------deferred_revenue according to over the expected life of the customer---------------------------
#     elif obj.productp_service.revenue_type.revenue_type == "over the expected life of the customer":

#         if obj.created_at > obj.productp_service.revenue_type.updated_at:
#             start_date = str(obj.tansaction.order_close_data)
#             start_date = parser.parse(start_date).date()
#             try:
#                 mth = ExpectedMonths.objects.get(
#                     company=obj.tansaction.user.company)
#                 mth = mth.months
#             except:
#                 mth = 0
#             # mth = obj.productp_service.revenue_type.months
#             end_date = start_date+relativedelta(months=mth)
#             delta = end_date - start_date
#             days = delta.days+1
#             revenue_calc = obj.total_revenue/days
#             value = obj.total_revenue

#             current_date = start_date
#             d = 0
#             while current_date <= end_date + relativedelta(days=1) or (end_date.month == current_date.month and end_date.year == current_date.year):
#                 revenue1 = {}
#                 days_in_month = calendar.monthrange(
#                     current_date.year, current_date.month)[1]
#                 revenue1['date'] = current_date.strftime("%b %y")
#                 value -= rev[d]['value']
#                 # if value < 1:
#                     # value = 0
#                 revenue1['value'] = value
#                 revenue_list_by_month.append(revenue1)
#                 current_date += relativedelta(months=1)
#                 d += 1
#             return revenue_list_by_month

#         else:
#             value = obj.total_revenue
#             close_date = CloseDate.objects.all().first()
#             close_date = parser.parse(str(close_date.close_date)).date()
#             start_date = str(obj.tansaction.order_close_data)
#             start_date = parser.parse(start_date).date()
#             try:
#                 mth = ExpectedMonths.objects.get(
#                     company=obj.tansaction.user.company)
#                 mth = mth.months
#             except:
#                 mth = 0
#             # mth = obj.productp_service.revenue_type.months
#             end_date = start_date+relativedelta(months=mth)
#             rp = 0
#             days_in_sub = 0
#             revenue_calc_ex = 0
#             if start_date > close_date:
#                 calc = Calculation.objects.get(items=obj)
#                 deffered_revenue = calc.deffered_revenue
#                 fixed_date = close_date-start_date
#                 fixed_months = delta.months+1
#                 current_date = start_date
#                 d = 0
#                 fixed_value = 0
#                 while current_date <= end_date + relativedelta(days=1) or (end_date.month == current_date.month and end_date.year == current_date.year):
#                     revenue1 = {}
#                     if d < fixed_months:
#                         revenue_list_by_month.append[deffered_revenue[d]]
#                         fixed_value += deffered_revenue[d]['value']
#                         current_date += relativedelta(months=1)
#                         new_date = current_date
#                         d += 1
#                     else:
#                         if rp < 1:
#                             delta = new_date - end_date
#                             days_in_sub = delta.days+1
#                             revenue_calc = (obj.total_revenue -
#                                             fixed_value)/days_in_sub
#                         days_in_month = calendar.monthrange(
#                             current_date.year, current_date.month)[1]
#                         revenue1['date'] = current_date.strftime("%b %y")
#                         value -= rev[d]['value']
#                         # if value < 1:
#                         #     value = 0
#                         revenue1['value'] = value
#                         revenue_list_by_month.append(revenue1)
#                         current_date += relativedelta(months=1)
#                         rp += 1
#                         d += 1
#                 return revenue_list_by_month

#             else:
#                 start_date = str(obj.tansaction.order_close_data)
#                 start_date = parser.parse(start_date).date()
#                 try:
#                     mth = ExpectedMonths.objects.get(
#                         company=obj.tansaction.user.company)
#                     mth = mth.months
#                 except:
#                     mth = 0
#                 mth = obj.productp_service.revenue_type.months
#                 end_date = start_date+relativedelta(months=mth)
#                 delta = end_date - start_date
#                 days = delta.days+1
#                 revenue_calc = obj.total_revenue/days
#                 value = obj.total_revenue
#                 current_date = start_date
#                 d = 0
#                 while current_date <= end_date + relativedelta(days=1) or (end_date.month == current_date.month and end_date.year == current_date.year):
#                     revenue1 = {}
#                     days_in_month = calendar.monthrange(
#                         current_date.year, current_date.month)[1]
#                     revenue1['date'] = current_date.strftime("%b %y")
#                     value -= rev[d]['value']
#                     # if value < 1:
#                     #     value = 0
#                     revenue1['value'] = value
#                     revenue_list_by_month.append(revenue1)
#                     current_date += relativedelta(months=1)
#                     d += 1
#                 return revenue_list_by_month

#     # ---------------------deferred_revenue according to Manual revenue recognition---------------------------
#     elif obj.productp_service.revenue_type.revenue_type == "Manual revenue recognition":
#         # revenue1 = {}
#         # start_date = obj.tansaction.order_close_data
#         # end_date = start_date+relativedelta(months=48)
#         # current_date = start_date
#         # value = obj.total_revenue
#         # d = 0
#         # while current_date <= end_date:
#         #     revenue1 = {}
#         #     days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]
#         #     revenue1['date']=current_date.strftime("%b %y")
#         #     value -= rev[d]['value']
#         #     if value < 1:
#         #         value = 0
#         #     revenue1['value']= value
#         #     revenue_list_by_month.append(revenue1)
#         #     current_date += relativedelta(months=1)
#         # return revenue_list_by_month
#         return []


def item_arr(obj):

    # print('item_arr == ',)
    start_date = str(obj.s_start_d)
    end_date = str(obj.s_end_d)
    start_date = parser.parse(start_date).date()
    end_date = parser.parse(end_date).date()
    delta = end_date - start_date
    days = delta.days+1
    arr_list_by_month = []
    arr = obj.total_revenue

    if start_date >= end_date:
        days_in_month = calendar.monthrange(
            start_date.year, start_date.month)[1]
        days = days_in_month*1

    result_date = start_date + relativedelta(months=+12)
    leap_days = (result_date - start_date).days
    value = arr/days*leap_days
   
    current_date = start_date
    while current_date < end_date + relativedelta(days=1):
        year = current_date.year

        if current_date.year == end_date.year and current_date.month == end_date.month:
            if calendar.monthrange(current_date.year, current_date.month)[1] > end_date.day:
                current_date += relativedelta(months=1)
                break

        if current_date.day != start_date.day:
            # If current_date not the same as date1.day, change it to the same day as date1.day
            try:
                current_date = current_date.replace(day=start_date.day)
            except:
                last_day_of_month = (current_date.replace(day=1) + relativedelta(months=1, days=-1)).day

                current_date = current_date.replace(day=last_day_of_month)        

        arr_dic = {}
        # date.append(current_date.strftime("%B %Y"))
        arr_dic['date'] = current_date.strftime("%b %y")
        arr_dic['update'] = False
        arr_dic['pending_arr'] = False
        arr_dic['missing_date'] = False
        arr_dic['value'] = value

  
        arr_list_by_month.append(arr_dic)
        if obj.cancel_date != None:
            if current_date >= obj.cancel_date.date():
                break
        current_date += relativedelta(months=1)

    return arr_list_by_month


def total_arr(obj):
    items = obj
    arr = []
    for i in range(0, len(items)):
        if items[i].total_revenue == 0:
            continue
        try:
            calculation = Calculation.objects.get(items=items[i])
        except:
            continue
        if calculation.arr == None:
            continue
        arr += calculation.arr

    result = []
    combined = {}
    for item in arr:
        if item["date"] in combined:
            combined[item["date"]]["value"] += item["value"]
            if item['update'] == True:
                combined[item["date"]]["update"] = True
            if item['pending_arr'] == True:
                combined[item["date"]]["pending_arr"] = True

        else:
            combined[item["date"]] = {
                "date": item["date"],
                "value": item["value"],
                "update": item["update"],
                # "missing_date": item["missing_date"]
                "missing_date": False,
                "addition": False,
                "pending_arr": item['pending_arr']
            }

    for _, value in combined.items():
        result.append(value)
        # if value['value'] != 0:
        # result.append(value)

    result.sort(key=lambda x: parse_date(x['date']))


    if result is not None and len(result) > 0:

        # Remove leading zeros
        while result and result[0]['value'] == 0:
            result = result[1:]

        # Remove trailing zeros
        while result and result[-1]['value'] == 0:
            result = result[:-1]

        pending = 0
        for i in range(len(result)):

            if result[i]['value'] == 0:
                if result[i-3]['pending_arr'] == False:
                    if pending < 3:

                        pending += 1
                        result[i]['value'] = result[i-1]['value']
                        result[i]['pending_arr'] = True
                        result[i]['update'] = True
            else:
                pending = 0
            if i == len(result)-1:
                lent = 3
                # if result[i]['pending_arr'] == True:
                #     lent = 2
                # if i > 1:
                #     if result[i-1]['pending_arr'] == True:
                #         lent = 1
                # if i > 2:
                #     if result[i-2]['pending_arr'] == True:
                #         lent = 0
                if result[i]['pending_arr'] == False:
                    new_date = parse_date(result[len(result)-1]["date"])
                    final_date = new_date.strftime("%b %y")
                    new_value = result[len(result)-1]["value"]
                    for k in range(lent):
                        new_date += relativedelta(months=1)
                        final_date = new_date.strftime("%b %y")
                        result.append({
                            "date": final_date,
                            "value": new_value,
                            "update": True,
                            "missing_date": False,
                            "addition": False,
                            "pending_arr": True

                        })

    if result is not None and len(result) > 0:
        last_item = len(result)-1

        new_date = parse_date(result[last_item]["date"])
        for i in range(3):
            new_date += relativedelta(months=1)
            final_date = new_date.strftime("%b %y")
            result.append({
                "date": final_date,
                "value": 0,
                "update": False,
                "missing_date": True,
                "addition": True,
                "pending_arr": False

            })

    # adding status on basis of compare the values
    for k, item in enumerate(result):
        # if item['update'] == True
        #     result[k]['status'] = "yellow"

        # if item["value"] > result[k-1]["value"] and item["value"] > result[k-2]["value"] and k > 0 and result[k-1]["value"] != 0:
        if item["value"] > result[k-1]["value"]:
            result[k]['status'] = "green"

        # elif item["value"] < result[k-1]["value"] and item["value"] < result[k-2]["value"] and k > 0 and item["value"] != 0:
        elif item["value"] < result[k-1]["value"]:
            result[k]['status'] = "red"
        else:
            result[k]['status'] = "black"

    if result is not None and len(result) > 0:
        all_dates = set(item['date'] for item in result)
        min_date = min(all_dates, key=parse_date)
        max_date = max(all_dates, key=parse_date)
        all_dates_with_zero = set(
            (parse_date(min_date) + timedelta(days=30*i)).strftime("%b %y")
            for i in range((parse_date(max_date) - parse_date(min_date)).days // 30 + 1)
        )
        missing_dates = all_dates_with_zero - all_dates
        result.extend([{"date": date, "value": 0, "missing_date": True,
                      "addition": False, "pending_arr": False} for date in missing_dates])

        result.sort(key=lambda x: parse_date(x['date']))
    
    # if "Middletown (OH) Division of Fire, City Of" == items[0].tansaction.customer_name:
    #     print(result, "::::::::::::::::::::::::::::::::::::::")
    #     print(1 +"i")

    return result


def total_pending_arr(obj):
    '''
    returning total pending off all customer
    '''
    items = obj
    arr = []
    for i in range(0, len(items)):
        if items[i].total_revenue == 0:
            continue
        try:
            calculation = Calculation.objects.get(items=items[i])
        except:
            continue
        if calculation.arr == None:
            continue
        arr += calculation.arr

    result = []
    combined = {}
    
    for item in arr:
        if item['pending_arr'] == True:
            if item["date"] in combined:
                combined[item["date"]]["value"] += item["value"]

            else:
                combined[item["date"]] = {
                    "date": item["date"],
                    "value": item["value"]
                }

    for _, value in combined.items():
        result.append(value)

    result.sort(key=lambda x: parse_date(x['date']))

    if result is not None and len(result) > 0:
        all_dates = set(item['date'] for item in result)
        min_date = min(all_dates, key=parse_date)
        max_date = max(all_dates, key=parse_date)
        all_dates_with_zero = set(
            (parse_date(min_date) + timedelta(days=30*i)).strftime("%b %y")
            for i in range((parse_date(max_date) - parse_date(min_date)).days // 30 + 1)
        )
        missing_dates = all_dates_with_zero - all_dates
        result.extend([{"date": date, "value": 0} for date in missing_dates])

        result.sort(key=lambda x: parse_date(x['date']))

    return result

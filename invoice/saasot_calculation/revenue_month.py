import calendar

from invoice.models import Transaction, Item, CalculationMonths, CloseDate
from services.models import ExpectedMonths

from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from dateutil import parser



def parse_date(date_str):
    # Parse the date string and return a datetime object
    date_obj = datetime.strptime(date_str, "%b %y")
    return date_obj

def revenue(obj):
    date = ""
    revenue_list_by_month = []

# ---------------------revenue according to over life of subscription---------------------------
    if obj.productp_service.revenue_type.revenue_type == "over life of subscription":
        start_date = parser.parse(str(obj.s_start_d)).date()
        end_date = parser.parse(str(obj.s_end_d)).date()
        delta = relativedelta(end_date, start_date)
        months = delta.years * 12 + delta.months + 1
        revenue_calc = obj.total_revenue/months

        current_date = start_date
        while current_date <= end_date:
            revenue = {}
            revenue['date']=current_date.strftime("%b %y")
            revenue['value']=revenue_calc
            revenue_list_by_month.append(revenue)
            current_date += relativedelta(months=1)
        return revenue_list_by_month

# ---------------------revenue according to immediately upon invoicing---------------------------
    elif obj.productp_service.revenue_type.revenue_type == "immediately upon invoicing":
        revenue = {}
        date = obj.tansaction.order_close_data
        revenue['date']=date.strftime("%b %y")
        revenue['value']=obj.total_revenue
        revenue_list_by_month.append(revenue)
        return revenue_list_by_month

# ---------------------revenue according to over the expected life of the customer---------------------------
    elif obj.productp_service.revenue_type.revenue_type == "over the expected life of the customer":
        
        if obj.created_at > obj.productp_service.revenue_type.updated_at:
            start_date = str(obj.tansaction.order_close_data)
            start_date = parser.parse(start_date).date()
            try:
                mth = ExpectedMonths.objects.get(company=obj.user.company)
            except:
                mth = 0
            # mth = obj.productp_service.revenue_type.months
            end_date = start_date+relativedelta(months=mth)
            delta = relativedelta(end_date, start_date)
            months = delta.years * 12 + delta.months + 1
            revenue_calc = obj.total_revenue/months

            current_date = start_date
            while current_date <= end_date:
                revenue = {}
                revenue['date']=current_date.strftime("%b %y")
                revenue['value']=revenue_calc
                revenue_list_by_month.append(revenue)
                current_date += relativedelta(months=1)
            return revenue_list_by_month
        else:
            close_date = CloseDate.objects.all().first()
            close_date = parser.parse(str(close_date.close_date)).date()
            start_date = str(obj.tansaction.order_close_data)
            start_date = parser.parse(start_date).date()
            try:
                mth = ExpectedMonths.objects.get(company=obj.user.company)
            except:
                mth = 0
            # mth = obj.productp_service.revenue_type.months
            end_date = start_date+relativedelta(months=mth)
            new_date = start_date
            rp = 0
            days_in_sub = 0
            revenue_calc_ex = 0
            if start_date < close_date:
                calc = CalculationMonths.objects.get(items=obj)
                revenue_calc = calc.revenue
                delta = relativedelta(close_date, start_date)
                fixed_months = delta.years * 12 + delta.months + 1
                current_date = start_date
                d = 0
                fixed_value = 0
                while current_date <= end_date:
                    revenue = {}
                    if d < fixed_months:
                        try:
                            revenue_list_by_month.append(revenue_calc[d])
                            fixed_value += revenue_calc[d]['value']
                        except:
                            revenue['date']=current_date.strftime("%b %y")
                            revenue['value']=0
                            revenue_list_by_month.append(revenue)
                        current_date += relativedelta(months=1)
                        new_date = current_date
                        d +=1
                    else:
                        if rp < 1:
                            delta = relativedelta(new_date, end_date)
                            months_in_sub = delta.years * 12 + delta.months + 1
                            revenue_calc_ex = (obj.total_revenue-fixed_value)/months_in_sub
                        revenue['date']=current_date.strftime("%b %y")
                        revenue['value']=revenue_calc_ex
                        revenue_list_by_month.append(revenue)
                        current_date += relativedelta(months=1)
                        rp +=1
                return revenue_list_by_month

            else:
                start_date = str(obj.tansaction.order_close_data)
                start_date = parser.parse(start_date).date()
                try:
                    mth = ExpectedMonths.objects.get(company=obj.user.company)
                except:
                    mth = 0
                # mth = obj.productp_service.revenue_type.months
                end_date = start_date+relativedelta(months=mth)
                delta = relativedelta(end_date, start_date)
                months = delta.years * 12 + delta.months + 1
                revenue_calc = obj.total_revenue/months

                current_date = start_date
                while current_date <= end_date:
                    revenue = {}
                    days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]
                    revenue['date']=current_date.strftime("%b %y")
                    revenue['value']=revenue_calc
                    revenue_list_by_month.append(revenue)
                    current_date += relativedelta(months=1)
                return revenue_list_by_month
    
    elif obj.productp_service.revenue_type.revenue_type == "Manual revenue recognition":
        # revenue = {}
        # start_date = obj.tansaction.order_close_data
        # end_date = start_date+relativedelta(months=48)
        # current_date = start_date
        # while current_date <= end_date:
        #     revenue = {}
        #     days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]
        #     revenue['date']=current_date.strftime("%b %y")
        #     revenue['value']= 0
        #     revenue_list_by_month.append(revenue)
        #     current_date += relativedelta(months=1)
        # return revenue_list_by_month
        return []

def billing(obj):
    date = ""
    revenue_list_by_month = []
    revenue = {}
    date = obj.tansaction.order_close_data
    revenue['date']=date.strftime("%b %y")
    revenue['value']=obj.amount
    revenue_list_by_month.append(revenue)
    return revenue_list_by_month

def deferred_revenue(obj):
    try:
        cal =  CalculationMonths.objects.get(items=obj)
        rev = cal.revenue
    except:
        rev = revenue(obj)
    revenue_list_by_month = []

# ---------------------deferred_revenue according to over life of subscription---------------------------
    if obj.productp_service.revenue_type.revenue_type == "over life of subscription":
        start_date = str(obj.s_start_d)
        end_date = str(obj.s_end_d)
        start_date = parser.parse(start_date).date()
        end_date = parser.parse(end_date).date()
        
        delta = relativedelta(end_date, start_date)
        months = delta.years * 12 + delta.months + 1
        revenue_calc = obj.total_revenue/months
        value = obj.total_revenue
            
        current_date = start_date
        d = 0
        while current_date <= end_date:
            revenue1 = {}
            revenue1['date']=current_date.strftime("%b %y")
            value -= rev[d]['value']
            if value < 1:
                value = 0
            revenue1['value']=value
            revenue_list_by_month.append(revenue1)
            current_date += relativedelta(months=1)
            d += 1
        return revenue_list_by_month

# ---------------------deferred_revenue according to immediately upon invoicing---------------------------
    elif obj.productp_service.revenue_type.revenue_type == "immediately upon invoicing":
        revenue1 = {}
        start_date = obj.tansaction.order_close_data
        end_date = start_date+relativedelta(months=48)
        current_date = start_date
        while current_date <= end_date:
            revenue1 = {}
            delta = relativedelta(end_date, start_date)
            months = delta.years * 12 + delta.months + 1
            revenue1['date']=current_date.strftime("%b %y")
            revenue1['value']=abs(obj.amount-obj.total_revenue)
            revenue_list_by_month.append(revenue1)
            current_date += relativedelta(months=1)
        return revenue_list_by_month

# ---------------------deferred_revenue according to over the expected life of the customer---------------------------
    elif obj.productp_service.revenue_type.revenue_type == "over the expected life of the customer":

        if obj.created_at > obj.productp_service.revenue_type.updated_at:
            start_date = str(obj.tansaction.order_close_data)
            start_date = parser.parse(start_date).date()
            try:
                mth = ExpectedMonths.objects.get(company=obj.user.company)
            except:
                mth = 0
            # mth = obj.productp_service.revenue_type.months
            end_date = start_date+relativedelta(months=mth)
            delta = relativedelta(end_date, start_date)
            months = delta.years * 12 + delta.months + 1
            revenue_calc = obj.total_revenue/months
            value = obj.total_revenue

            current_date = start_date
            d = 0
            while current_date <= end_date:
                revenue1 = {}
                revenue1['date']=current_date.strftime("%b %y")
                value -= rev[d]['value']
                if value < 1:
                    value = 0
                revenue1['value']=value
                revenue_list_by_month.append(revenue1)
                current_date += relativedelta(months=1)
                d += 1
            return revenue_list_by_month

        else:
            value = obj.total_revenue
            close_date = CloseDate.objects.all().first()
            close_date = parser.parse(str(close_date.close_date)).date()
            start_date = str(obj.tansaction.order_close_data)
            start_date = parser.parse(start_date).date()
            try:
                mth = ExpectedMonths.objects.get(company=obj.user.company)
            except:
                mth = 0
            # mth = obj.productp_service.revenue_type.months
            end_date = start_date+relativedelta(months=mth)
            rp = 0
            days_in_sub = 0
            revenue_calc_ex = 0
            if start_date > close_date:
                calc = CalculationMonths.objects.get(items=obj)
                deffered_revenue = calc.deffered_revenue
                fixed_date = close_date-start_date
                fixed_months = delta.months+1
                current_date = start_date
                d = 0
                fixed_value = 0
                while current_date < end_date:
                    revenue1 = {}
                    if d < fixed_months:
                        revenue_list_by_month.append[deffered_revenue[d]]
                        fixed_value += deffered_revenue[d]['value']
                        current_date += relativedelta(months=1)
                        new_date = current_date
                        d +=1
                    else:
                        if rp < 1:
                            delta = relativedelta(new_date, end_date)
                            months_in_sub = delta.years * 12 + delta.months + 1
                            revenue_calc_ex = (obj.total_revenue-fixed_value)/months_in_sub
                        revenue1['date']=current_date.strftime("%b %y")
                        value -= rev[d]['value']
                        if value < 1:
                            value = 0
                        revenue1['value']=value
                        revenue_list_by_month.append(revenue1)
                        current_date += relativedelta(months=1)
                        rp += 1

                return revenue_list_by_month

            else:
                start_date = str(obj.tansaction.order_close_data)
                start_date = parser.parse(start_date).date()
                try:
                    mth = ExpectedMonths.objects.get(company=obj.user.company)
                except:
                    mth = 0
                # mth = obj.productp_service.revenue_type.months
                end_date = start_date+relativedelta(months=mth)
                delta = relativedelta(end_date, start_date)
                months = delta.years * 12 + delta.months + 1
                revenue_calc = obj.total_revenue/months
                value = obj.total_revenue
                
                current_date = start_date
                d = 0
                while current_date <= end_date:
                    revenue1 = {}
                    revenue1['date']=current_date.strftime("%b %y")
                    value -= rev[d]['value']
                    if value < 1:
                        value = 0
                    revenue1['value']=value
                    revenue_list_by_month.append(revenue1)
                    current_date += relativedelta(months=1)
                    d += 1
                return revenue_list_by_month
    
# ---------------------deferred_revenue according to Manual revenue recognition---------------------------
    elif obj.productp_service.revenue_type.revenue_type == "Manual revenue recognition":
        return []
        # revenue1 = {}
        # start_date = obj.tansaction.order_close_data
        # end_date = start_date+relativedelta(months=48)
        # current_date = start_date
        # value = obj.total_revenue
        # while current_date <= end_date:
        #     revenue1 = {}
        #     days_in_month = calendar.monthrange(current_date.year, current_date.month)[1]
        #     revenue1['date']=current_date.strftime("%b %y")
        #     value -= rev[d]['value']
        #     if value < 1:
        #         value = 0
        #     revenue1['value']= value
        #     revenue_list_by_month.append(revenue1)
        #     current_date += relativedelta(months=1)
        # return revenue_list_by_month

def item_arr(obj):
    start_date = str(obj.s_start_d)
    end_date = str(obj.s_end_d)
    start_date = parser.parse(start_date).date()
    end_date = parser.parse(end_date).date()
    delta = relativedelta(end_date, start_date)
    months = delta.years * 12 + delta.months + 1
    arr_list_by_month = []
    arr = 0
    arr = obj.total_revenue

    current_date = start_date
    while current_date <= end_date:
        year = current_date.year
        feb_29 = False
        
        # Check if February has 29 days for the current year
        if current_date.month == 2:
            try:
                datetime(year, 2, 29)
                feb_29 = True
            except ValueError:
                feb_29 = False
        arr_dic = {}
        # date.append(current_date.strftime("%B %Y"))
        arr_dic['date']=current_date.strftime("%b %y")
        arr_dic['update'] = False
        if feb_29 == True:
            arr_dic['value']=arr/months*12
        else:
            arr_dic['value']=arr/months*12
        arr_list_by_month.append(arr_dic)
        if  obj.cancel_date != None:
            if current_date >=  obj.cancel_date.date():
                break
        current_date += relativedelta(months=1)
    return arr_list_by_month
    
def total_arr(obj):
    items = obj
    arr = []
    for i in range(0, len(items)):
        try:
            calculation = CalculationMonths.objects.get(items=items[i])
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
        else:
            combined[item["date"]] = {
                "date": item["date"],
                "value": item["value"],
                "update": item["update"]
            }

    for _, value in combined.items():
        result.append(value)

    for k, item in enumerate(result):
        # if item['update'] == True
        #     result[k]['status'] = "yellow"
    
        if item["value"] > result[k-1]["value"] and item["value"] > result[k-2]["value"] and k > 0 and result[k-1]["value"] != 0:
            result[k]['status'] = "green"

        elif item["value"] < result[k-1]["value"] and item["value"] < result[k-2]["value"] and k > 0 and item["value"] != 0:
            result[k]['status'] = "red"
        else:
            result[k]['status'] = "black"

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
            calculation = CalculationMonths.objects.get(items=items[i])
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


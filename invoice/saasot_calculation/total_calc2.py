from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def parse_date(date_str):
    '''
    Parse the date string and return a datetime object
    '''
    date_obj = datetime.strptime(date_str, "%b %y")
    return date_obj

def table_totals(data):
    '''
    calculating total of revenue , billing , deffered reveneue for multiple transaction.
    '''
    total_revenue =[]
    total_billing_revenue = []
    total_arr = []
    balance = [] 

    for tsc in range(0, len(data)):
        for i in range(0, len(data[tsc]['items'])):
            combined = {}

    # -------------------- calculate total_revenue -------------------
            for item in total_revenue:
                combined[item['date']] = combined.get(item['date'], 0) + item['value']

            for item in data[tsc]['items'][i]['revenue']['revenue']:
                combined[item['date']] = combined.get(item['date'], 0) + item['value']

            total_revenue = [{"date": date, "value": value} for date, value in combined.items()]

            if len(total_revenue)>0:
                # Add missing month with 0 value
                all_dates = set(item['date'] for item in total_revenue)
                min_date = min(all_dates, key=parse_date)
                max_date = max(all_dates, key=parse_date)
                all_dates_with_zero = set(
                    (parse_date(min_date) + timedelta(days=30*i)).strftime("%b %y")
                    for i in range((parse_date(max_date) - parse_date(min_date)).days // 30 + 1)
                )
                missing_dates = all_dates_with_zero - all_dates
                total_revenue.extend([{"date": date, "value": 0} for date in missing_dates])

                total_revenue.sort(key=lambda x: parse_date(x['date']))

    # -------------------- calculate total_billing_revenue--------------------
            combined = {}
            for item in total_billing_revenue:
                combined[item['date']] = combined.get(item['date'], 0) + item['value']

            for item in data[tsc]['items'][i]['billing']['billing']:
                combined[item['date']] = combined.get(item['date'], 0) + item['value']

            total_billing_revenue = [{"date": date, "value": value} for date, value in combined.items()]

            if len(total_billing_revenue)>0:
                 # Add missing month with 0 value
                 all_dates = set(item['date'] for item in total_billing_revenue)
                 min_date = min(all_dates, key=parse_date)
                 max_date = max(all_dates, key=parse_date)
                 all_dates_with_zero = set(
                     (parse_date(min_date) + timedelta(days=30*i)).strftime("%b %y")
                     for i in range((parse_date(max_date) - parse_date(min_date)).days // 30 + 1)
                 )
                 missing_dates = all_dates_with_zero - all_dates
                 total_billing_revenue.extend([{"date": date, "value": 0} for date in missing_dates])

                 total_billing_revenue.sort(key=lambda x: parse_date(x['date']))

    # -------------------- calculate balance--------------------
            combined = {}
            for item in balance:
                combined[item['date']] = combined.get(item['date'], 0) + item['value']

            if data[tsc]['items'][i]['revenue_type'] == "immediately upon invoicing":
                for item in data[tsc]['items'][i]['deffered_revenue']['deffered_revenue']:
                    combined[item['date']] = combined.get(item['date'], 0) - item['value']
            else:
                for item in data[tsc]['items'][i]['deffered_revenue']['deffered_revenue']:
                    combined[item['date']] = combined.get(item['date'], 0) + item['value']

            balance = [{"date": date, "value": value} for date, value in combined.items()]
            
            if len(balance)>0:
                # Add missing month with 0 value
                all_dates = set(item['date'] for item in balance)
                min_date = min(all_dates, key=parse_date)
                max_date = max(all_dates, key=parse_date)
                all_dates_with_zero = set(
                    (parse_date(min_date) + timedelta(days=30*i)).strftime("%b %y")
                    for i in range((parse_date(max_date) - parse_date(min_date)).days // 30 + 1)
                )
                missing_dates = all_dates_with_zero - all_dates
                balance.extend([{"date": date, "value": 0} for date in missing_dates])

                balance.sort(key=lambda x: parse_date(x['date']))
# -------------------- calculate total_arr--------------------
            combined = {}
            # for item in total_arr:
            #     combined[item['date']] = combined.get(item['date'], 0) + item['value']

            # if data[tsc]['items'][i]['item_arr']['arr'] != None:
            #     for item in data[tsc]['items'][i]['item_arr']['arr']:
            #         combined[item['date']] = combined.get(item['date'], 0) + item['value']

            #     total_arr = [{"date": date, "value": value} for date, value in combined.items()]
            if data[tsc]['items'][i]['item_arr']['arr']:
                for item in data[tsc]['items'][i]['item_arr']['arr']:

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
                    total_arr = [value for date, value in combined.items()]

            # for _, value in combined.items():
            #     result.append(value)

            # Add missing month with 0 value
            if len(total_arr)>0:
                all_dates = set(item['date'] for item in total_arr)
                min_date = min(all_dates, key=parse_date)
                max_date = max(all_dates, key=parse_date)
                all_dates_with_zero = set(
                    (parse_date(min_date) + timedelta(days=30*i)).strftime("%b %y")
                    for i in range((parse_date(max_date) - parse_date(min_date)).days // 30 + 1)
                )
                missing_dates = all_dates_with_zero - all_dates
                total_arr.extend([{"date": date, "value": 0} for date in missing_dates])

                total_arr.sort(key=lambda x: parse_date(x['date']))

# -------------------- calculate total_cumilative_revenue--------------------
    total_cumilative_revenue = []
    value = 0
    for i in range(0, len(total_revenue)):
        date = total_revenue[i]['date']
        value += total_revenue[i]['value']
        total_cumilative_revenue.append({"date": date, "value": value})

# -------------------- calculate total_cumilative_billing--------------------
    total_cumilative_billing = []
    value = 0
    for i in range(0, len(total_billing_revenue)):
        date = total_billing_revenue[i]['date']
        value += total_billing_revenue[i]['value']
        total_cumilative_billing.append({"date": date, "value": value})

    return({
        "temp_total_revenue": total_revenue,
        "total_billing_revenue": total_billing_revenue,
        "balance": balance,
        "total_cumilative_revenue":total_cumilative_revenue,
        "total_cumilative_billing": total_cumilative_billing,
        "total_arr": total_arr
    })

def items_totals(data):
    '''
    calultating total revenue , deffered revenue and abiiling basis on product type
    '''
    total_items_rev = {}
    total_items_arr = {}
    total_items_def = {}
    total_items_bal = {}
    duplicate = []
    dupli = []
    table_headings = []
    table_heading = {}
    t_r = 0
    total_it = []
    d = 0
    for tsc in range(0, len(data)):
        d += 1
        for i in range(0, len(data[tsc]['items'])):
            
    # -------------------- calculate total_items_rev--------------------
            t_r = data[tsc]['items'][i]['total_revenue']
            if data[tsc]['items'][i]['heading']["productp_service_type"] not in duplicate:
                total_items_rev[data[tsc]['items'][i]['heading']["productp_service_type"]] = []
                total_it = data[tsc]['items'][i]['revenue']['revenue']
            else:
                total_it = total_items_rev[data[tsc]['items'][i]['heading']["productp_service_type"]]
            if data[tsc]['items'][i]['heading']["productp_service_type"] not in dupli:
                for k in range(0, len(data[tsc]['items'])):
                    if data[tsc]['items'][i]['heading']["productp_service_type"] not in duplicate:
                        if i!=k:
                            combined = {}
                            if data[tsc]['items'][i]['heading']["productp_service_type"] == data[tsc]['items'][k]['heading']["productp_service_type"]: 
                                # t_r += data[tsc]['items'][i]['total_revenue']
                                for item in total_it:
                                    combined[item['date']] = combined.get(item['date'], 0) + item['value']
                                for item in data[tsc]['items'][k]['revenue']['revenue']:
                                    combined[item['date']] = combined.get(item['date'], 0) + item['value']

                                total_it = [{"date": date, "value": value} for date, value in combined.items()]

                            if len(total_it)>0:
                            # Add missing month with 0 value
                                all_dates = set(item['date'] for item in total_it)
                                min_date = min(all_dates, key=parse_date)
                                max_date = max(all_dates, key=parse_date)
                                all_dates_with_zero = set(
                                    (parse_date(min_date) + timedelta(days=30*i)).strftime("%b %y")
                                    for i in range((parse_date(max_date) - parse_date(min_date)).   days // 30 + 1)
                                )
                                missing_dates = all_dates_with_zero - all_dates
                                total_it.extend([{"date": date, "value": 0} for date in missing_dates])

                                total_it.sort(key=lambda x: parse_date(x['date']))
                    else:
                        combined = {}
                        if data[tsc]['items'][i]['heading']["productp_service_type"] == data[tsc]['items'][k]['heading']["productp_service_type"]: 
                            # t_r += data[tsc]['items'][i]['total_revenue']
                            for item in total_it:
                                combined[item['date']] = combined.get(item['date'], 0) + item['value']
                            for item in data[tsc]['items'][k]['revenue']['revenue']:
                                combined[item['date']] = combined.get(item['date'], 0) + item['value']

                            total_it = [{"date": date, "value": value} for date, value in combined.items()]

                    if len(total_it)>0:
                        # Add missing month with 0 value
                        all_dates = set(item['date'] for item in total_it)
                        min_date = min(all_dates, key=parse_date)
                        max_date = max(all_dates, key=parse_date)
                        all_dates_with_zero = set(
                                (parse_date(min_date) + timedelta(days=30*i)).strftime("%b %y")
                            for i in range((parse_date(max_date) - parse_date(min_date)).days // 30 + 1)
                        )
                        missing_dates = all_dates_with_zero - all_dates
                        total_it.extend([{"date": date, "value": 0} for date in missing_dates])
                        total_it.sort(key=lambda x: parse_date(x['date']))

            table_heading[data[tsc]['items'][i]['heading']["productp_service_type"]] = t_r
            total_items_rev[data[tsc]['items'][i]['heading']["productp_service_type"]] = total_it
            total_it = []

    # -------------------- calculate total_items_def--------------------

            if data[tsc]['items'][i]['heading']["productp_service_type"] not in duplicate:
                total_items_def[data[tsc]['items'][i]['heading']["productp_service_type"]] = []
                total_it = data[tsc]['items'][i]['deffered_revenue']['deffered_revenue']
            else:
                total_it = total_items_def[data[tsc]['items'][i]['heading']["productp_service_type"]]
            if data[tsc]['items'][i]['heading']["productp_service_type"] not in dupli:
                for k in range(0, len(data[tsc]['items'])):
                    if data[tsc]['items'][i]['heading']["productp_service_type"] not in duplicate:
                        if i!=k:
                            combined = {}
                            if data[tsc]['items'][i]['heading']["productp_service_type"] == data[tsc]['items'][k]['heading']["productp_service_type"]: 
                                for item in total_it:
                                    combined[item['date']] = combined.get(item['date'], 0) + item['value']
                                for item in data[tsc]['items'][k]['deffered_revenue']['deffered_revenue']:
                                    combined[item['date']] = combined.get(item['date'], 0) + item['value']

                                total_it = [{"date": date, "value": value} for date, value in combined.items()]

                            if len(total_it)>0:
                                # Add missing month with 0 value
                                all_dates = set(item['date'] for item in total_it)
                                min_date = min(all_dates, key=parse_date)
                                max_date = max(all_dates, key=parse_date)
                                all_dates_with_zero = set(
                                    (parse_date(min_date) + timedelta(days=30*i)).strftime("%b %y")
                                    for i in range((parse_date(max_date) - parse_date(min_date)).days // 30 + 1)
                                )
                                missing_dates = all_dates_with_zero - all_dates
                                total_it.extend([{"date": date, "value": 0} for date in missing_dates])

                                total_it.sort(key=lambda x: parse_date(x['date']))
                    else:
                        combined = {}
                        if data[tsc]['items'][i]['heading']["productp_service_type"] == data[tsc]['items'][k]['heading']["productp_service_type"]: 
                            for item in total_it:
                                combined[item['date']] = combined.get(item['date'], 0) + item['value']
                            for item in data[tsc]['items'][k]['deffered_revenue']['deffered_revenue']:
                                combined[item['date']] = combined.get(item['date'], 0) + item['value']

                            total_it = [{"date": date, "value": value} for date, value in combined.items()]

                        if len(total_it)>0:
                            # Add missing month with 0 value
                            all_dates = set(item['date'] for item in total_it)
                            min_date = min(all_dates, key=parse_date)
                            max_date = max(all_dates, key=parse_date)
                            all_dates_with_zero = set(
                                (parse_date(min_date) + timedelta(days=30*i)).strftime("%b %y")
                                for i in range((parse_date(max_date) - parse_date(min_date)).days // 30 + 1)
                            )
                            missing_dates = all_dates_with_zero - all_dates
                            total_it.extend([{"date": date, "value": 0} for date in missing_dates])

                            total_it.sort(key=lambda x: parse_date(x['date']))
            
           
            total_items_def[data[tsc]['items'][i]['heading']["productp_service_type"]] = total_it
            total_it = []

    # -------------------- calculate total_items_billing--------------------
            if data[tsc]['items'][i]['heading']["productp_service_type"] not in duplicate:
                total_items_bal[data[tsc]['items'][i]['heading']["productp_service_type"]] = []
                total_it = data[tsc]['items'][i]['billing']['billing']
            else:
                total_it = total_items_bal[data[tsc]['items'][i]['heading']["productp_service_type"]]
            if data[tsc]['items'][i]['heading']["productp_service_type"] not in dupli:
                for k in range(0, len(data[tsc]['items'])):
                    if data[tsc]['items'][i]['heading']["productp_service_type"] not in duplicate:
                        if i!=k:
                            combined = {}
                            if data[tsc]['items'][i]['heading']["productp_service_type"] == data[tsc]['items'][k]['heading']["productp_service_type"]: 
                                for item in total_it:
                                    combined[item['date']] = combined.get(item['date'], 0) + item['value']
                                for item in data[tsc]['items'][k]['billing']['billing']:
                                    combined[item['date']] = combined.get(item['date'], 0) + item['value']

                                total_it = [{"date": date, "value": value} for date, value in combined.items()]
                                
                            if len(total_it)>0:
                                # Add missing month with 0 value
                                all_dates = set(item['date'] for item in total_it)
                                min_date = min(all_dates, key=parse_date)
                                max_date = max(all_dates, key=parse_date)
                                all_dates_with_zero = set(
                                    (parse_date(min_date) + timedelta(days=30*i)).strftime("%b %y")
                                    for i in range((parse_date(max_date) - parse_date(min_date)).days // 30 + 1)
                                )
                                missing_dates = all_dates_with_zero - all_dates
                                total_it.extend([{"date": date, "value": 0} for date in missing_dates])

                                total_it.sort(key=lambda x: parse_date(x['date']))
                    else:
                        combined = {}
                        if data[tsc]['items'][i]['heading']["productp_service_type"] == data[tsc]['items'][k]['heading']["productp_service_type"]: 
                            for item in total_it:
                                combined[item['date']] = combined.get(item['date'], 0) + item['value']
                            for item in data[tsc]['items'][k]['billing']['billing']:
                                combined[item['date']] = combined.get(item['date'], 0) + item['value']

                            total_it = [{"date": date, "value": value} for date, value in combined.items()]

                        if len(total_it)>0:
                            # Add missing month with 0 value
                            all_dates = set(item['date'] for item in total_it)
                            min_date = min(all_dates, key=parse_date)
                            max_date = max(all_dates, key=parse_date)
                            all_dates_with_zero = set(
                                (parse_date(min_date) + timedelta(days=30*i)).strftime("%b %y")
                                for i in range((parse_date(max_date) - parse_date(min_date)).days // 30 + 1)
                            )
                            missing_dates = all_dates_with_zero - all_dates
                            total_it.extend([{"date": date, "value": 0} for date in missing_dates])

                            total_it.sort(key=lambda x: parse_date(x['date']))
            
           
            total_items_bal[data[tsc]['items'][i]['heading']["productp_service_type"]] = total_it
            total_it = []


    # -------------------- calculate total_items_arr--------------------
            if data[tsc]['items'][i]['heading']["productp_service_type"] not in duplicate:
                total_items_arr[data[tsc]['items'][i]['heading']["productp_service_type"]] = []
                if data[tsc]['items'][i]['item_arr']['arr'] != None:
                    total_it = data[tsc]['items'][i]['item_arr']['arr']
            else:
                total_it = total_items_arr[data[tsc]['items'][i]['heading']["productp_service_type"]]
            if data[tsc]['items'][i]['heading']["productp_service_type"] not in dupli:
                for k in range(0, len(data[tsc]['items'])):
                    if data[tsc]['items'][i]['heading']["productp_service_type"] not in duplicate:
                        if i!=k:
                            combined = {}
                            if data[tsc]['items'][i]['heading']["productp_service_type"] == data[tsc]['items'][k]['heading']["productp_service_type"]: 
                                for item in total_it:
                                    combined[item['date']] = combined.get(item['date'], 0) + item['value']
                                if data[tsc]['items'][i]['item_arr']['arr'] != None:
                                    for item in data[tsc]['items'][k]['item_arr']['arr']:
                                        combined[item['date']] = combined.get(item['date'], 0) + item['value']

                                total_it = [{"date": date, "value": value} for date, value in combined.items()]
                    else:
                        combined = {}
                        if data[tsc]['items'][i]['heading']["productp_service_type"] == data[tsc]['items'][k]['heading']["productp_service_type"]: 
                            for item in total_it:
                                combined[item['date']] = combined.get(item['date'], 0) + item['value']
                            if data[tsc]['items'][i]['item_arr']['arr'] != None:
                                for item in data[tsc]['items'][k]['item_arr']['arr']:
                                    combined[item['date']] = combined.get(item['date'], 0) + item['value']

                            total_it = [{"date": date, "value": value} for date, value in combined.items()]
           
            total_items_arr[data[tsc]['items'][i]['heading']["productp_service_type"]] = total_it
            total_it = []

            duplicate.append(data[tsc]['items'][i]['heading']["productp_service_type"])
            dupli.append(data[tsc]['items'][i]['heading']["productp_service_type"])
        dupli = []

# ------------------------------table heading------------------------------
    # table_headings = total_items_rev.keys()
    for first_key, first_value in  table_heading.items():
                table_headings.append({first_key:first_value})


    return(
        {
        "total_items_rev": total_items_rev,
        "total_items_def": total_items_def,
        "total_items_bal": total_items_bal,
        # "table_headings": list(set(table_headings)),
        "table_headings":table_headings,
        "total_items_arr": total_items_arr
        }
    )

def ending_arr(data):
    keys = data.keys()
    ending = []

    for key in keys:
        combined = {}
        for item in ending:
            combined[item['date']] = combined.get(item['date'], 0) + item['value']
        
        for item in data[key]:
            if key == "exp_Logos" or key == "con_Logos":
               continue
            # else:
            combined[item['date']] = combined.get(item['date'], 0) + item['value']

        ending = [{"date": date, "value": value} for date, value in combined.items()]

        ending.sort(key=lambda x: parse_date(x['date']))

    return ending

def arr_rollforward(data):
    metrics = {
        "new": {},
        "beggining_bal": {},
        "expansion": {},
        "churn": {},
        "recovery": {},
        "contraction": {},
        "pending": {}
    }
    hover = {
    "new_hover": [],
    "beggining_hover": [],
    "expansion_hover": [],
    "churn_hover": [],
    "recovery_hover": [],
    "contraction_hover": [],
    "pending_hover": []
    }
    logo_rollforward = {}
    key_metcrics= {}
    contrat = []

    for i in range(len(data)):
        customer_name = data[i]["customer_name"]
        ids = data[i]["ids"]
        arr = data[i]["arr"]
        skip_0 = 0 
        churn_0 = 0
# ----------------------------ARR ROLLFORWARD----------------------------
        for k, item in enumerate(arr):
            date = item["date"]
            value = item["value"]
            prev_value = arr[k - 1]["value"] if k > 0 else 0
            prev_prev_value = arr[k - 2]["value"] if k > 1 else 0
            prev_prev_prev_value =arr[k - 3]["value"] if k > 2 else 0
            
            if value !=0:
                skip_0 += 1
            # calculating new arr
            if skip_0 == 1 and churn_0 == 0:
                metrics["new"][date] = metrics["new"].get(date, 0) + value
                hover['new_hover'].append({"date":item["date"], "value": item["value"], "customer_name": data[i]["customer_name"], "ids": data[i]["ids"]})

            # calculating beggining_bal arr
            if k > 0 and skip_0 > 1:
                if value == prev_value and data[i]["arr"][k]["addition"] == False and data[i]["arr"][k]["missing_date"] == False:
                    # if k+3 <= len(arr)-1 or value != 0:
                    metrics["beggining_bal"][date] = metrics["beggining_bal"].get(date, 0) + value
                    hover['beggining_hover'].append({"date":item["date"], "value": item["value"], "customer_name": data[i]["customer_name"], "ids": data[i]["ids"]})
            
            # calculating expansion arr
            if k > 0 and skip_0 > 1:
                try:
                    # if (value > prev_value and ((prev_value > 0) or (prev_prev_value > 0) or (prev_prev_prev_value > 0))) or (value > prev_value and data[i]["arr"][k-1]["missing_date"] == False):
                    if value > prev_value:
                        if prev_value > 0 or (prev_prev_value > 0 and data[i]["arr"][k-2]["pending_arr"] == False) or (prev_prev_prev_value > 0 and data[i]["arr"][k-3]["pending_arr"] == False):
                            metrics["expansion"][date] = metrics["expansion"].get(date, 0) + (value - prev_value)
                            metrics["beggining_bal"][date] = metrics["beggining_bal"].get(date, 0) + prev_value
                            hover['expansion_hover'].append({"date":item["date"], "value": item['value']-data[i]["arr"][k-1]["value"], "customer_name": data[i]["customer_name"], "ids": data[i]["ids"]})
                            hover['beggining_hover'].append({"date":item["date"], "value": data[i]["arr"][k-1]["value"], "customer_name": data[i]["customer_name"], "ids": data[i]["ids"]})
                except:
                    pass

            # calculating churn arr
            try:
                if prev_value > 0:
                    # if (value == 0 and (data[i]["arr"][k+1]["value"] == 0) and data[i]["arr"][k+2]["value"] == 0 and data[i]["arr"][k]["addition"] == True) or (data[i]["arr"][k-1]["pending_arr"] == True and value == 0):
                    # if ((value == 0 and (data[i]["arr"][k]["addition"] == True or data[i]["arr"][k]["missing_date"] == True)) and (data[i]["arr"][k+1]["value"] == 0) and data[i]["arr"][k+2]["value"] == 0) or (data[i]["arr"][k-1]["pending_arr"] == True and value == 0 and (data[i]["arr"][k]["missing_date"]==True or data[i]["arr"][k]["addition"] == True)):
                    if ((value == 0 and (data[i]["arr"][k]["addition"] == True or data[i]["arr"][k]["missing_date"] == True)) and (data[i]["arr"][k+1]["value"] == 0) and data[i]["arr"][k+2]["value"] == 0) or data[i]["arr"][k-1]["pending_arr"] == True and value == 0:
                        churn_value = prev_value
                        if value < 0:
                            churn_value = prev_value
        
                        metrics["churn"][date] = metrics["churn"].get(date, 0) - churn_value
                        metrics["beggining_bal"][date] = metrics["beggining_bal"].get(date, 0) + prev_value
                        hover['beggining_hover'].append({"date":item["date"], "value": churn_value, "customer_name": data[i]["customer_name"], "ids": data[i]["ids"]})
                        hover['churn_hover'].append({"date":item["date"], "value": churn_value, "customer_name": data[i]["customer_name"], "ids": data[i]["ids"]})
                        skip_0 = 0
                        churn_0 += 1
            except Exception as e:
                pass        
                
            # if len(arr) == k+1:
            #     churn_data = parse_date(date)
            #     churn_data += relativedelta(months=1)
            #     new_churn_data = churn_data.strftime("%b %y")
            #     churn_value = value
            #     if value < 0:
            #         churn_value = value

            #     if item['date'] == 'Jan 23':
            #         contrat.append(value)


            #     print(churn_value, "=================================================")
            #     metrics["churn"][new_churn_data] = metrics["churn"].get(new_churn_data, 0) - churn_value
            #     metrics["beggining_bal"][new_churn_data] = metrics["beggining_bal"].get(new_churn_data, 0) + value
            #     hover['beggining_hover'].append({"date":new_churn_data, "value": churn_value, "customer_name": data[i]["customer_name"], "ids": data[i]["ids"]})
            #     hover['churn_hover'].append({"date":new_churn_data, "value": churn_value, "customer_name": data[i]["customer_name"], "ids": data[i]["ids"]})


            # calculating recovery arr
            if k > 0 and (skip_0 > 1 or churn_0 > 0):
                try:
                    # if value > 0 and prev_value == 0 and (prev_prev_value == 0 or data[i]["arr"][k-2]["pending_arr"] == True) and data[i]["arr"][k-1]["missing_date"] == True:
                    if value > 0 and prev_value == 0 and (prev_prev_value == 0 or data[i]["arr"][k-2]["pending_arr"] == True):
                        if k > 2:
                            if data[i]["arr"][k-3]["value"] == 0 or data[i]["arr"][k-3]["pending_arr"] == True:
                                metrics["recovery"][date] = metrics["recovery"].get(date, 0) + value
                                hover['recovery_hover'].append({"date":item["date"], "value": item["value"], "customer_name": data[i]["customer_name"], "ids": data[i]["ids"]})
                except:
                    pass

            # calculating contraction arr
            if k > 0 and skip_0 > 1:
                if value < prev_value:
                    try:
                        # if (value != 0 or (data[i]["arr"][k+1]["value"] != 0 and data[i]["arr"][k-1]["pending_arr"] == False) or (data[i]["arr"][k+2]["value"] != 0 and data[i]["arr"][k-2]["pending_arr"] == False)) or ((data[i]["arr"][k]["missing_date"] == False or data[i]["arr"][k+1]["missing_date"] ==False or data[i]["arr"][k+2]["missing_date"] == False) and data[i]["arr"][k+1]["addition"] == False):
                        # if (value != 0 or (data[i]["arr"][k+1]["value"] != 0 and data[i]["arr"][k-1]["pending_arr"] == False) or (data[i]["arr"][k+2]["value"] != 0 and data[i]["arr"][k-2]["pending_arr"] == False)):
                        # if (value == 0 and data[i]["arr"][k-1]["pending_arr"] == False) or value !=0 or (value == 0 and data[i]["arr"][k-1]["pending_arr"] == True and data[i]["arr"][k]["missing_date"] == False and data[i]["arr"][k]["addition"] == False):
                        if (value == 0 and data[i]["arr"][k-1]["pending_arr"] == False) or value !=0:

                            metrics["contraction"][date] = metrics["contraction"].get(date, 0) + (value - prev_value)
                            metrics["beggining_bal"][date] = metrics["beggining_bal"].get(date, 0) + prev_value
                            hover['contraction_hover'].append({"date":item["date"], "value": item['value']-data[i]["arr"][k-1]["value"], "customer_name": data[i]["customer_name"], "ids": data[i]["ids"]})
                            hover['beggining_hover'].append({"date":item["date"], "value": data[i]["arr"][k-1]["value"], "customer_name": data[i]["customer_name"], "ids": data[i]["ids"]})

                    except:
                        metrics["contraction"][date] = metrics["contraction"].get(date, 0) + (value - prev_value)
                        metrics["beggining_bal"][date] = metrics["beggining_bal"].get(date, 0) + prev_value
                        hover['contraction_hover'].append({"date":item["date"], "value": item['value']-data[i]["arr"][k-1]["value"], "customer_name": data[i]["customer_name"], "ids": data[i]["ids"]})
                        hover['beggining_hover'].append({"date":item["date"], "value": data[i]["arr"][k-1]["value"], "customer_name": data[i]["customer_name"], "ids": data[i]["ids"]})
            
    for metric, metric_data in metrics.items():
        sorted_metric = [{"date": date, "value": value} for date, value in metric_data.items()]
        sorted_metric.sort(key=lambda x: parse_date(x['date']))
        metrics[metric] = sorted_metric
    
    for key, value in hover.items():
        hover[key].sort(key=lambda x: parse_date(x['date']))
    
    metrics['ending'] = ending_arr(metrics)

# -------------------------LOGO ROLLFORWARD-------------------------

    #calculating beggining logo
    # print(hover['beggining_hover'], ":::::::::::::::")
    date_counts = {}
    for item in hover['beggining_hover']:
        date = item["date"]
        if date in date_counts:
            date_counts[date] += 1
        else:
            date_counts[date] = 1

    logo_rollforward['Beginning_Logos'] = [{"date": date, "value": count} for date, count in date_counts.items()]

    #calculating new logo
    date_counts = {}
    for item in hover['new_hover']:
        date = item["date"]
        if date in date_counts:
            date_counts[date] += 1
        else:
            date_counts[date] = 1

    logo_rollforward['New_Logos'] = [{"date": date, "value": count} for date, count in date_counts.items()]

    date_counts = {}
    for item in hover['recovery_hover']:
        date = item["date"]
        if date in date_counts:
            date_counts[date] += 1
        else:
            date_counts[date] = 1

    logo_rollforward['Recovery_Logos'] = [{"date": date, "value": count} for date, count in date_counts.items()]

    #calculating churn_logos
    date_counts = {}
    for item in hover['churn_hover']:
        date = item["date"]
        if date in date_counts:
            date_counts[date] -= -(-1)
        else:
            date_counts[date] = -1

    logo_rollforward['Churn_Logos'] = [{"date": date, "value": count} for date, count in date_counts.items()]


    date_counts = {}
    for item in hover['contraction_hover']:
        date = item["date"]
        if date in date_counts:
            date_counts[date] -= -(-1)
        else:
            date_counts[date] = -1

    logo_rollforward['con_Logos'] = [{"date": date, "value": count} for date, count in date_counts.items()]

    date_counts = {}
    for item in hover['expansion_hover']:
        date = item["date"]
        if date in date_counts:
            date_counts[date] += 1
        else:
            date_counts[date] = 1

    logo_rollforward['exp_Logos'] = [{"date": date, "value": count} for date, count in date_counts.items()]


    #calculating ending_logo
    ending_logos = ending_arr(logo_rollforward)
    logo_rollforward['Ending_Logos'] = ending_logos



# -------------------------key metrics---------------------------------------------
    Avg_New_Arr = []
    combined = {}
    for i in range(len(metrics['new'])):
        combined['date'] = metrics['new'][i]['date']
        combined['value'] = metrics['new'][i]['value']/logo_rollforward['New_Logos'][i]['value']
        Avg_New_Arr.append(combined)
        combined = {}
    key_metcrics['Avg_New_Arr'] = Avg_New_Arr

    # Avg_End_Arr 
    Avg_End_Arr = []
    combined = {}
    for i in range(len(metrics['ending'])):
        combined['date'] = metrics['ending'][i]['date']
        try:
            combined['value'] = metrics['ending'][i]['value']/logo_rollforward['Ending_Logos'][i]['value']
            Avg_End_Arr.append(combined)
        except:
            pass
        combined = {}
    key_metcrics['Avg_End_Arr'] = Avg_End_Arr

    try:
        # Add missing month with 0 value
        new_churn = metrics['churn']
        all_dates = set(item['date'] for item in metrics['beggining_bal'])
        min_date = min(all_dates, key=parse_date)
        max_date = max(all_dates, key=parse_date)
        all_dates_with_zero = set(
            (parse_date(min_date) + timedelta(days=30*i)).strftime("%b %y")
            for i in range((parse_date(max_date) - parse_date(min_date)).days // 30 + 1)
        )
        churn_dates = set(item['date'] for item in new_churn)
        missing_dates = all_dates_with_zero - churn_dates
        new_churn.extend([{"date": date, "value": 0} for date in missing_dates])

        new_churn.sort(key=lambda x: parse_date(x['date']))
    except:
        new_churn = []

    # Arr_Churn_Period  
    combined = {}
    arr_churn_period = []
    arr_churn_rolling = []
    arr_churn_12 = []

    for i, item in enumerate(new_churn):
        try:
            check = metrics['beggining_bal'][i]['value']
        except:
            continue
        if item['value'] < 0:
            combined['date'] = item['date']
            combined['value'] = abs((item['value'] / metrics['beggining_bal'][i]['value'] * 12) * 100)
            arr_churn_period.append(combined)
            combined = {}
            
        if i > 2:
            combined['date'] = item['date']
            try:
                combined['value'] = abs(((item['value'] + new_churn[i - 1]['value'] + new_churn[i - 2]['value']) / metrics['beggining_bal'][i - 2]['value'] * 4) * 100)
            except:
                combined['value'] = 0
            arr_churn_rolling.append(combined)
            combined = {}
            
        if i > 11:
            combined['date'] = item['date']
            churn_last_12 = i
            value = 0
            while churn_last_12 >= 0:
                value += new_churn[churn_last_12]['value']
                churn_last_12 -= 1
            try:
                combined['value'] = abs(value / metrics['beggining_bal'][i - 11]['value'] * 100)
            except:
                combined['value'] = 0
            arr_churn_12.append(combined)
            
        combined = {}
    key_metcrics['Arr_churn_period'] = arr_churn_period
    key_metcrics['Arr_churn_rolling'] = arr_churn_rolling
    key_metcrics['Arr_churn_12'] = arr_churn_12



    try:
        new_churn_logos = logo_rollforward['Churn_Logos']
        all_dates = set(item['date'] for item in  logo_rollforward['Beggining_Logos'])
        min_date = min(all_dates, key=parse_date)
        max_date = max(all_dates, key=parse_date)
        all_dates_with_zero = set(
            (parse_date(min_date) + timedelta(days=30*i)).strftime("%b %y")
            for i in range((parse_date(max_date) - parse_date(min_date)).days // 30 + 1)
        )
        churn_dates = set(item['date'] for item in new_churn_logos)
        missing_dates = all_dates_with_zero - churn_dates
        new_churn_logos.extend([{"date": date, "value": 0} for date in missing_dates])

        new_churn_logos.sort(key=lambda x: parse_date(x['date']))
    except:
        new_churn_logos = []


    # -------------------------------------- logo_Churn_Period_ --------------------------------------
    logo_churn_period = []
    logo_churn_rolling = []
    logo_churn_12 = []

    combined = {}
    for i, item in enumerate(new_churn_logos):
        if item['value']>0:
            combined['date'] = item['date']
            combined['value'] = abs((item['value']/logo_rollforward['Beggining_Logos'][i]['value']*12)*100)
            logo_churn_period.append(combined)
            combined = {}

    # -------------------------------------- logo_churn_rolling --------------------------------------
        if i>2:
            combined['date'] = item['date']
            try:
                combined['value'] = abs(((item['value']+new_churn_logos[i-1]['value']+new_churn_logos[i-2]['value'])/logo_rollforward['Beggining_Logos'][i-2]['value']*4)*100)
            except:
                combined['value'] = 0
            logo_churn_rolling.append(combined)
            combined = {}

# -------------------------------------- logo_churn_12 --------------------------------------
        if i>11:
            combined['date'] = item['date']
            churn_last_12 = i
            value = 0
            while churn_last_12 >= 0:
                value += new_churn_logos[churn_last_12]['value']
                churn_last_12 -= 1
            try:
                combined['value'] = abs(value/logo_rollforward['Beggining_Logos'][i-11]['value']*100)
            except:
                combined['value'] = 0
            logo_churn_12.append(combined)
            combined = {}
    key_metcrics['Logo_churn_12'] = logo_churn_12
    key_metcrics['Logo_churn_rolling'] = logo_churn_rolling
    key_metcrics['Logo_churn_period'] = logo_churn_period


    return{
        "Beginning_ARR": metrics['beggining_bal'],
        "beggining_hover": hover['beggining_hover'], "New_ARR": metrics['new'],
        "new_hover": hover['new_hover'],
        "Recovery_ARR": metrics['recovery'], "recovery_hover": hover['recovery_hover'],
        "Expansion_ARR": metrics['expansion'],
        "expansion_hover": hover['expansion_hover'],
        "Contraction_ARR": metrics['contraction'],
        "contraction_hover": hover['contraction_hover'],
        "Churn_ARR": metrics['churn'], "churn_hover": hover['churn_hover'],
        "Pending_ARR": metrics['pending'], "Pending_hover": hover['pending_hover'],
        "Ending_ARR": metrics['ending'],
        "Logo_Rollforward": logo_rollforward,
        "key_metcrics": key_metcrics,
    }




def total_arr_customer(data):
    total_arr = []  
    for i in range(0, len(data)):
        combined = {}

# -------------------- calculate total_revenue--------------------
        for item in total_arr:
            combined[item['date']] = combined.get(item['date'], 0) + item['value']

        for item in data[i]['arr']:
            combined[item['date']] = combined.get(item['date'], 0) + item['value']

        total_arr = [{"date": date, "value": value} for date, value in combined.items()]

        # Add missing month with 0 value
        all_dates = set(item['date'] for item in total_arr)
        min_date = min(all_dates, key=parse_date)
        max_date = max(all_dates, key=parse_date)
        all_dates_with_zero = set(
            (parse_date(min_date) + timedelta(days=30*i)).strftime("%b %y")
            for i in range((parse_date(max_date) - parse_date(min_date)).days // 30 + 1)
        )
        missing_dates = all_dates_with_zero - all_dates
        total_arr.extend([{"date": date, "value": 0} for date in missing_dates])

        total_arr.sort(key=lambda x: parse_date(x['date']))
        
    return total_arr


def peding_arr(data):
    '''
    returning total pending arr on months and list of customer
    '''
    peding_arr = {}
    pending_hover = []
    for i in range(len(data)):
        customer_name = data[i]["customer_name"]
        ids = data[i]["ids"]
        arr = data[i]["arr"]

# ----------------------------ARR ROLLFORWARD----------------------------
        for k, item in enumerate(arr):
            date = item["date"]
            value = item["value"]

            peding_arr[date] = peding_arr.get(date, 0) + value
            pending_hover.append({"date":item["date"], "value": item["value"], "customer_name": data[i]["customer_name"], "ids": data[i]["ids"]})
    
    peding_arr = [{"date": date, "value": value} for date, value in peding_arr.items()]
    peding_arr.sort(key=lambda x: parse_date(x['date']))
    pending_hover.sort(key=lambda x: parse_date(x['date']))
    peding_arr = peding_arr

    return {
        "Pennding_ARR":peding_arr,
        "Pending_Hover": pending_hover
    }

import pandas as pd
from datetime import datetime, timedelta
from dateutil import relativedelta, parser
from .models import Transaction, Item
from services.models import ProductService
from django.utils import timezone
from .signals import*
import logging
from dateutil.relativedelta import relativedelta

def extract_clean_data(file) -> pd.DataFrame:
    try:
        df=pd.read_excel(file, keep_default_na=False)
        df['Customer'] = df['Customer'].apply(str)
        df['Transaction Type'] = df['Transaction Type'].apply(str)
        try:
            df['Number'] = df['Invoice Number'].apply(int)
        except:
            df['Number'] = df['Number'].apply(int)
        df['Product/Service'] = df['Product/Service'].apply(str)
        df['Memo/Description'] = df['Memo/Description'].apply(str)
        df['Account'] = df['Account'].apply(str)
        df['Class'] = df['Class'].apply(str)
        df['Qty'] = df['Qty'].map(lambda x: int(x) if  x != '' else 0)
        df['Sales Price'] = df['Sales Price'].map(lambda x: float(x) if  x != '' else 0)
        df['Amount'] = df['Amount'].map(lambda x: float(x) if  x != '' else 0)

        df['Subscription Start Date'] =  df['Subscription Start Date'].map(lambda x: str(x) if  x != '' else None)
        # df['Subscription Start Date'] = df['Subscription Start Date'].apply(lambda x: timezone.make_aware(x) if pd.notnull(x) else None)

        df['Subscription End Date'] =  df['Subscription End Date'].map(lambda x: str(x) if  x != '' else None)
        # df['Subscription End Date'] = df['Subscription End Date'].apply(lambda x: timezone.make_aware(x) if pd.notnull(x) else None)

        def convert_integer_to_datetime(x):
            if isinstance(x, int):
                # Assuming 43102 is the integer representation of a date
                integer_date = x

                # Base date for Excel date representation
                base_date = datetime(1899, 12, 30)

                # Calculate the date
                date_value = base_date + timedelta(days=integer_date)

                return date_value
            elif isinstance(x, str):
                # If it's already a string, try converting it to a datetime
                try:
                    return pd.to_datetime(x, errors='coerce')
                except ValueError:
                    return None
            else:
                return x
        try:
            df['Date'] = df['Invoice Date'].apply(lambda x: convert_integer_to_datetime(x))
        except:
            df['Date'] = df['Date'].apply(lambda x: convert_integer_to_datetime(x))

        return  df
    except Exception as e:
        print(e, "(((((((((((((((((())))))))))))))))))")
        return {'error': e}

# Yesterday
def load_membership_data(file, user, company):
    if not company:
        company = user.company
    
    tmp_data = extract_clean_data(file)
    
    # Log the tmp_data for debugging
    logging.debug(f"tmp_data: {tmp_data}")
    
    try:
        if tmp_data.get('error'):
            return tmp_data
    except Exception as e:
        print(f"Error checking tmp_data for 'error' key: {e}")
        return {'error': 'An unexpected error occurred while processing the data.'}
    
    try:
        result = insert_item_to_db(tmp_data, user, company)
    except Exception as e:
        print(f"Error inserting data into database: {e}")
        return {'error': 'An error occurred while inserting data into the database.'}
        # return {'message': 'Successfully Upload'}
    
    return result


# load data into django model
def insert_item_to_db(tmp_data, user, company):

    print('============ Company ==============', company)
    item_info = []
    numberss = []
    correct_csv_date = []
    num = Transaction.objects.filter(company=company).values_list('invoice_number')
    # num = Transaction.objects.filter(user__company= user.company).values_list('invoice_number')
    for i in range(0, len(num)):
        numberss.append(num[i][0])

    # print('()()()()() ()()()()() Num')
    # print(num)

    productservice = ProductService.objects.filter(company=company)

    # Fetch active product services
    productservice = ProductService.objects.filter(company=company)
    product_name_list = [ps.product_name for ps in productservice if ps.is_active]
    undefiend_service = [ps.product_name for ps in productservice if not ps.is_active]
    
    undefiend_service_info = []
    
    print('Insert Into DB')
    print('===================')
    print(numberss)

    for _, row in tmp_data.iterrows():
        
        print('Insert Into DB entered in for') 
        # if (row['Customer'] == 'Branford (CT) Fire Department, Town of'):            
        red_flag = False
        subcription_status = None
        subscription_terms_month = None
        start_date = None
        end_date = None
        arr = None
        if pd.notnull(row['Subscription End Date']) and pd.notnull(row['Subscription Start Date']):
            print('Insert Into DB Product/Servicess')
            arr = row['Amount']
            try:
                start_date = datetime.strptime(row['Subscription Start Date'], "%Y-%m-%d %H:%M:%S")
                end_date = datetime.strptime(row['Subscription End Date'], "%Y-%m-%d %H:%M:%S")
            except:   
                Start_Date = int(row['Subscription Start Date'])
                Start_Date_base = datetime(1899, 12, 30)  # Excel's base date is 1900-01-00, but there's a leap year bug, so we use 1899-12-30 
                end_date = int(row['Subscription End Date'])
                end_date_base =  datetime(1899, 12, 30)

                start_date = Start_Date_base + timedelta(days=Start_Date)
                end_date = end_date_base + timedelta(days=end_date)

            delta = relativedelta(end_date, start_date)
            subscription_terms_month = delta.years * 12 + delta.months+1
            # subscription_terms_month = delta.years * 12 + delta.months
            
            if datetime.now() < end_date:
                subcription_status = "active"
            else:
                subcription_status = "pending renewal"# Or any other default value you prefer

        #split customer name
        customer_name = row['Customer'].split(':')
        cus_name = customer_name[0]
        if customer_name[0][-1] == ".":
            cus_name = customer_name[0][:-1]

        if row['Product/Service'] in product_name_list:
            productp_service = ProductService.objects.get(company=company, product_name = row['Product/Service'])
            
            print('Insert Into DB Product/Service 1')

            if productp_service is not None and productp_service.revenue_type is not None and productp_service.revenue_type.revenue_type == "over life of subscription" and (row['Subscription Start Date'] is None or row['Subscription End Date'] is None):
                correct_csv_date.append(row['Number'])
                print('Insert Into DB Product/Service 2')

            else:
                print('Insert Into DB Product/Service else')
                if row['Number'] in numberss:
                    if len(customer_name)>1:
                        transaction = Transaction.objects.filter(
                            user__company = company, invoice_number = row['Number'],
                            customer_name__iexact=cus_name, order_close_data=row['Date']
                            ).first()
                    else:
                        transaction = Transaction.objects.filter(
                            user__company = company, invoice_number = row['Number'],
                            customer_name__iexact=customer_name[0], order_close_data=row['Date']
                            ).first()
                    if transaction:
                        if Item.objects.filter(item_description=row['Memo/Description'], quantity=abs(row['Qty']), 
                            subscription_terms_month=subscription_terms_month, productp_service=productp_service,
                            tansaction=transaction, total_revenue=row['Amount'], sale_price=row['Sales Price']).exists():
                            continue
                        else:
                            item_info.append(
                                Item(
                                    item_description = row['Memo/Description'],
                                    quantity = abs(row['Qty']),
                                    s_start_d = start_date,
                                    s_end_d = end_date,
                                    subscription_terms_month = subscription_terms_month,
                                    arr = arr if arr is not None else None,
                                    subscription_status = subcription_status,
                                    total_revenue = row['Amount'] if row['Amount'] is not None else None,
                                    productp_service = productp_service,
                                    tansaction = transaction,
                                    amount = row['Amount'] if row['Amount'] is not None else None,
                                    sale_price = row['Sales Price'] if row['Sales Price'] is not None else None,
                                )
                            )
                    else:

                        print('Insert Into DB else')

                        if len(customer_name)>1:
                            custom_name = cus_name
                        else:
                            custom_name = customer_name[0]

                        red_flag = True
                        transaction = Transaction.objects.create( customer_name = custom_name,
                            f_cst_name = custom_name,
                            order_close_data = row['Date'],
                            billing_method = row['Transaction Type'],
                            invoice_number = row['Number'],
                            user = user,
                            company = company,
                            red_flag = red_flag
                        )
                        # transaction = Transaction.objects.get(user__company = user.company, invoice_number = row['Number'])
                        item_info.append(
                            Item(
                                item_description = row['Memo/Description'],
                                quantity = abs(row['Qty']),
                                s_start_d = start_date,
                                s_end_d = end_date,
                                subscription_terms_month = subscription_terms_month,
                                arr = arr if arr is not None else None,
                                subscription_status = subcription_status,
                                total_revenue = row['Amount'] if row['Amount'] is not None else None,
                                productp_service = productp_service,
                                tansaction = transaction,
                                amount = row['Amount'] if row['Amount'] is not None else None,
                                sale_price = row['Sales Price'] if row['Sales Price'] is not None else None,
                            )
                        )
                else:
                    print('Insert Into DB else 2')
                    numberss.append(row['Number'])
                    if len(customer_name)>1:
                        print('Insert Into DB if 1') 
                        Transaction.objects.create( customer_name = cus_name,
                                f_cst_name = customer_name[1],
                                order_close_data = row['Date'],
                                billing_method = row['Transaction Type'],
                                invoice_number = row['Number'],
                                user = user,
                                company = company,
                                red_flag = red_flag
                            )
                    else:
                        print('Insert Into DB else 1') 
                        Transaction.objects.create( customer_name = customer_name[0],
                                order_close_data = row['Date'],
                                billing_method = row['Transaction Type'],
                                invoice_number = row['Number'],
                                user = user,
                                company = company,
                                red_flag = red_flag
                            )

                    transactions = Transaction.objects.filter(user__company=company, invoice_number=row['Number'])
                    if transactions.exists():
                        for transaction in transactions:
                            try:
                                item_info.append(
                                    Item(
                                        item_description=row['Memo/Description'],
                                        quantity=abs(row['Qty']),
                                        s_start_d=start_date,
                                        s_end_d=end_date,
                                        subscription_terms_month=subscription_terms_month,
                                        arr=arr if arr is not None else None,
                                        subscription_status=subcription_status,
                                        total_revenue=row['Amount'] if row['Amount'] is not None else None,
                                        productp_service=productp_service,
                                        tansaction=transaction,
                                        amount=row['Amount'] if row['Amount'] is not None else None,
                                        sale_price=row['Sales Price'] if row['Sales Price'] is not None else None,
                                    )
                                )
                            except Exception as e:
                                print('transaction Exception ks',e)
                                pass
        else:
            print('Else')

            if row['Product/Service'] in undefiend_service:
                pass
            else:
                undefiend_service.append(row['Product/Service'])
                undefiend_service_info.append(
                    ProductService(
                        product_name = row['Product/Service'],
                        is_active = False,
                        user = user,
                        company = company
                    )
            )
    
    # print('::::::::::::::::::::::::: Here item_info :::::::::::::::::::::::::::::::')
    # print(item_info)
    
    ProductService.objects.bulk_create(undefiend_service_info)
    itemss = Item.objects.bulk_create(item_info)
    for instance in itemss:
        calculation_on_item_save(sender=Item, instance=instance, created=True)

    return {"message":"Please correct the date in this invoices here or change product service", "correct_csv_date": correct_csv_date}




# # Live 2-July-Backup
# # load data into django model
# def load_membership_data(file, user, company):
    
#     if not company:
#         company = user.company
#     tmp_data = extract_clean_data(file)
#     try:
#         if tmp_data.get('error'):
#             return tmp_data
#     except:
#         pass

#     # threading.Thread(target=insert_item_to_db, args=[tmp_data, user]).start()
#     return insert_item_to_db(tmp_data, user, company)
#     # return {"message":"Done"}

# from dateutil import parser
# # load data into django model
# def insert_item_to_db(tmp_data, user, company):

#     print('============ Company ==============', company)
#     item_info = []
#     numberss = []
#     correct_csv_date = []
#     num = Transaction.objects.filter(company=company).values_list('invoice_number')
#     # num = Transaction.objects.filter(user__company= user.company).values_list('invoice_number')
#     for i in range(0, len(num)):
#         numberss.append(num[i][0])

#     productservice = ProductService.objects.filter(company=company)

#     product_name_list = []
#     undefiend_service = []
#     undefiend_service_info = []
#     for i in range(0,len(productservice)):
#         if productservice[i].is_active == True:
#             product_name_list.append(productservice[i].product_name)
#         else:
#             undefiend_service.append(productservice[i].product_name)
    
#     print('Insert Into DB')
    
#     for _, row in tmp_data.iterrows():
        
#         # print('Insert Into DB entered in for') 
#         # if (row['Customer'] == 'Branford (CT) Fire Department, Town of'):            
#         red_flag = False
#         subcription_status = None
#         subscription_terms_month = None
#         start_date = None
#         end_date = None
#         arr = None
#         if pd.notnull(row['Subscription End Date']) and pd.notnull(row['Subscription Start Date']):
#             # print('Insert Into DB Product/Servicess')
#             arr = row['Amount']
#             try:
#                 start_date = datetime.strptime(row['Subscription Start Date'], "%Y-%m-%d %H:%M:%S")
#                 end_date = datetime.strptime(row['Subscription End Date'], "%Y-%m-%d %H:%M:%S")
#             except:   
#                 Start_Date = int(row['Subscription Start Date'])
#                 Start_Date_base = datetime(1899, 12, 30)  # Excel's base date is 1900-01-00, but there's a leap year bug, so we use 1899-12-30 
#                 end_date = int(row['Subscription End Date'])
#                 end_date_base =  datetime(1899, 12, 30)

#                 start_date = Start_Date_base + timedelta(days=Start_Date)
#                 end_date = end_date_base + timedelta(days=end_date)

#             delta = relativedelta(end_date, start_date)
#             subscription_terms_month = delta.years * 12 + delta.months+1
#             # subscription_terms_month = delta.years * 12 + delta.months
            
#             if datetime.now() < end_date:
#                 subcription_status = "active"
#             else:
#                 subcription_status = "pending renewal"# Or any other default value you prefer

#         #split customer name
#         customer_name = row['Customer'].split(':')
#         cus_name = customer_name[0]
#         if customer_name[0][-1] == ".":
#             cus_name = customer_name[0][:-1]

#         if row['Product/Service'] in product_name_list:
#             productp_service = ProductService.objects.get(company=company, product_name = row['Product/Service'])
            
#             # print('Insert Into DB Product/Service 1')

#             if productp_service is not None and productp_service.revenue_type is not None and productp_service.revenue_type.revenue_type == "over life of subscription" and (row['Subscription Start Date'] is None or row['Subscription End Date'] is None):
#                 correct_csv_date.append(row['Number'])
#                 # print('Insert Into DB Product/Service 2')

#             else:
#                 # print('Insert Into DB Product/Service else')
#                 if row['Number'] in numberss:
#                     if len(customer_name)>1:
#                         transaction = Transaction.objects.filter(
#                             user__company = company, invoice_number = row['Number'],
#                             customer_name__iexact=cus_name, order_close_data=row['Date']
#                             ).first()
#                     else:
#                         transaction = Transaction.objects.filter(
#                             user__company = company, invoice_number = row['Number'],
#                             customer_name__iexact=customer_name[0], order_close_data=row['Date']
#                             ).first()
#                     if transaction:
#                         if Item.objects.filter(item_description=row['Memo/Description'], quantity=abs(row['Qty']), 
#                             subscription_terms_month=subscription_terms_month, productp_service=productp_service,
#                             tansaction=transaction, total_revenue=row['Amount'], sale_price=row['Sales Price']).exists():
#                             continue
#                         else:
#                             item_info.append(
#                                 Item(
#                                     item_description = row['Memo/Description'],
#                                     quantity = abs(row['Qty']),
#                                     s_start_d = start_date,
#                                     s_end_d = end_date,
#                                     subscription_terms_month = subscription_terms_month,
#                                     arr = arr if arr is not None else None,
#                                     subscription_status = subcription_status,
#                                     total_revenue = row['Amount'] if row['Amount'] is not None else None,
#                                     productp_service = productp_service,
#                                     tansaction = transaction,
#                                     amount = row['Amount'] if row['Amount'] is not None else None,
#                                     sale_price = row['Sales Price'] if row['Sales Price'] is not None else None,
#                                 )
#                             )
#                     else:

#                         # print('Insert Into DB else')

#                         if len(customer_name)>1:
#                             custom_name = cus_name
#                         else:
#                             custom_name = customer_name[0]

#                         red_flag = True
#                         transaction = Transaction.objects.create( customer_name = custom_name,
#                         f_cst_name = custom_name,
#                         order_close_data = row['Date'],
#                         billing_method = row['Transaction Type'],
#                         invoice_number = row['Number'],
#                         user = user,
#                         company = company,
#                         red_flag = red_flag
#                         )
#                         # transaction = Transaction.objects.get(user__company = user.company, invoice_number = row['Number'])
#                         item_info.append(
#                         Item(
#                             item_description = row['Memo/Description'],
#                             quantity = abs(row['Qty']),
#                             s_start_d = start_date,
#                             s_end_d = end_date,
#                             subscription_terms_month = subscription_terms_month,
#                             arr = arr if arr is not None else None,
#                             subscription_status = subcription_status,
#                             total_revenue = row['Amount'] if row['Amount'] is not None else None,
#                             productp_service = productp_service,
#                             tansaction = transaction,
#                             amount = row['Amount'] if row['Amount'] is not None else None,
#                             sale_price = row['Sales Price'] if row['Sales Price'] is not None else None,
#                         )
#                         )    
#                 else:
#                     # print('Insert Into DB else 2')
#                     numberss.append(row['Number'])
#                     if len(customer_name)>1:
#                         # print('Insert Into DB if 1') 
#                         Transaction.objects.create( customer_name = cus_name,
#                                 f_cst_name = customer_name[1],
#                                 order_close_data = row['Date'],
#                                 billing_method = row['Transaction Type'],
#                                 invoice_number = row['Number'],
#                                 user = user,
#                                 company = company,
#                                 red_flag = red_flag
#                                 )
#                     else:
#                         # print('Insert Into DB else 1') 
#                         Transaction.objects.create( customer_name = customer_name[0],
#                                 order_close_data = row['Date'],
#                                 billing_method = row['Transaction Type'],
#                                 invoice_number = row['Number'],
#                                 user = user,
#                                 company = company,
#                                 red_flag = red_flag
#                                 )

#                     transactions = Transaction.objects.filter(user__company=company, invoice_number=row['Number'])

#                     if transactions.exists():
#                         for transaction in transactions:
#                             # item_info.append(
#                             #     Item(
#                             #         item_description=row['Memo/Description'],
#                             #         quantity=abs(row['Qty']),
#                             #         s_start_d=start_date,
#                             #         s_end_d=end_date,
#                             #         subscription_terms_month=subscription_terms_month,
#                             #         arr=arr if arr is not None else None,
#                             #         subscription_status=subcription_status,
#                             #         total_revenue=row['Amount'] if row['Amount'] is not None else None,
#                             #         productp_service=productp_service,
#                             #         transaction=transaction,
#                             #         amount=row['Amount'] if row['Amount'] is not None else None,
#                             #         sale_price=row['Sales Price'] if row['Sales Price'] is not None else None,
#                             #     )
#                             # )

#                             try:
#                                 item_info.append(
#                                     Item(
#                                         item_description=row['Memo/Description'],
#                                         quantity=abs(row['Qty']),
#                                         s_start_d=start_date,
#                                         s_end_d=end_date,
#                                         subscription_terms_month=subscription_terms_month,
#                                         arr=arr if arr is not None else None,
#                                         subscription_status=subcription_status,
#                                         total_revenue=row['Amount'] if row['Amount'] is not None else None,
#                                         productp_service=productp_service,
#                                         transaction=transaction,
#                                         amount=row['Amount'] if row['Amount'] is not None else None,
#                                         sale_price=row['Sales Price'] if row['Sales Price'] is not None else None,
#                                     )
#                                 )
#                             except Exception as e:
#                                 print('transaction Exception ks',e)
#                                 pass
#         else:
#             # print('Else')

#             if row['Product/Service'] in undefiend_service:
#                 pass
#             else:
#                 undefiend_service.append(row['Product/Service'])
#                 undefiend_service_info.append(
#                     ProductService(
#                     product_name = row['Product/Service'],
#                     is_active = False,
#                     user = user,
#                     company = company
#                     )
#             )
    
#     ProductService.objects.bulk_create(undefiend_service_info)
#     itemss = Item.objects.bulk_create(item_info)
#     for instance in itemss:
#         calculation_on_item_save(sender=Item, instance=instance, created=True)

#     return {"message":"Please correct the date in this invoices here or change product service", "correct_csv_date": correct_csv_date}

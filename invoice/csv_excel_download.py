import pandas as pd
import io


# def sort_colums_by_date(df):
#     # Get date columns
#     # Get date columns
#     per_colums = ['customer name', 'INVOICE DATE', 'INVOICE NUMBER', 'Product/Service',
#                    'Product/Type', 'Qty', 'Sales Pric', 'SUBSCRIPTION START DATE', 'SUBSCRIPTION END DATE']

#     date_columns = [col for col in df.columns if col not in per_colums]

#     # Convert date columns to actual date objects for sorting
#     date_columns = sorted(date_columns, key=lambda x: pd.to_datetime(x, format='%b %y'))

#     # Reorder columns in the DataFrame based on the sorted date columns
#     df = df[per_colums + date_columns]

#     # Format date columns back to strings, but only for datetime columns
#     for col in date_columns:
#         if col in df.columns:
#             df[col] = df[col].apply(lambda x: x.strftime('%b %y') if pd.notnull(x) and isinstance(x, pd.Timestamp) else x)

#     return df

def sort_colums_by_date(df):
    # Get non-date columns
    non_date_columns = ['customer name', 'INVOICE DATE', 'INVOICE NUMBER', 'Product/Service',
                        'Product/Type', 'Qty', 'Sales Pric', 'SUBSCRIPTION START DATE', 'SUBSCRIPTION END DATE']

    # Get date columns
    date_columns = [col for col in df.columns if col not in non_date_columns]

    # Convert date columns to actual date objects for sorting
    date_columns = sorted(date_columns, key=lambda x: pd.to_datetime(x, format='%b %y'))

    # Extract years and months from date columns
    years_months = set((d.year, d.month) for d in pd.to_datetime(date_columns, format='%b %y'))

    # Generate all months between the minimum and maximum dates
    min_date = min(years_months, key=lambda x: (x[0], x[1]))
    max_date = max(years_months, key=lambda x: (x[0], x[1]))
    all_months = pd.date_range(start=f"{min_date[0]}-{min_date[1]}", end=f"{max_date[0]}-{max_date[1]}", freq='MS')

    # Convert back to string representation
    all_months_str = [month.strftime('%b %y') for month in all_months]

    # Reorder columns in the DataFrame based on the sorted date columns
    all_columns = non_date_columns + all_months_str
    df = df.reindex(columns=all_columns)


    # # Format date columns back to strings
    # for col in date_columns:
    #     df[col] = df[col].apply(lambda x: x.strftime('%b %y') if pd.notnull(x) and isinstance(x, pd.Timestamp) else x)

    return df




def create_arr_csv(data, username):

    # Create a list of dictionaries for each customer's data
    delimiter = ' '
    rows = []
    print("hala lulia hala luliahala luliahala luliahala luliahala luliahala lulia")
    for entry in data:
        row = {'customer name': entry['customer_name']}
        for record in entry['arr']:
            row[record['date']] = record['value']
        rows.append(row)
        
    df = pd.DataFrame(rows)

    df.columns = df.columns.str.replace(' ', '_')

    df = df.applymap(lambda x: f'"{x}"' if isinstance(x, str) and ' ' in x else x)

     # Save the DataFrame to a CSV file
    csv_filename = f'{username}-arr.csv'
    df.to_csv(csv_filename, index=False)

    # Create a ZIP file containing the CSV file
    # zip_file_path = csv_filename.replace('.csv', '.zip')
    # with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    #     zipf.write(csv_filename, os.path.basename(csv_filename))

    # Return the paths of the generated CSV and ZIP files
    return csv_filename


    # file = df.to_csv(index=False)
    # return file


def create_arr_excel(data, username):

    # Create a list of dictionaries for each customer's data
    rows = []
    for entry in data:
        row = {'customer name': entry['customer_name']}
        for record in entry['arr']:
            row[record['date']] = record['value']
        rows.append(row)
        
    df = pd.DataFrame(rows)

    # Get date columns
    date_columns = [col for col in df.columns if col != 'customer name']

    # Convert date columns to actual date objects for sorting
    date_columns = sorted(date_columns, key=lambda x: pd.to_datetime(x, format='%b %y'))

    # Reorder columns in the DataFrame based on the sorted date columns
    df = df[['customer name'] + date_columns]

    # Format date columns back to strings, but only for datetime columns
    for col in date_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x.strftime('%b %y') if pd.notnull(x) and isinstance(x, pd.Timestamp) else x)

    
    # Create an in-memory Excel file
    excel_file = io.BytesIO()
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    
    # Seek back to the beginning of the stream
    excel_file.seek(0)

    excel_filename = f'{username}-arr.xlsx'
    zip_filename = f'{username}-arr.zip'

    # Save the Excel file with the username as the filename
    with open(excel_filename, 'wb') as file:
        file.write(excel_file.read())

    # # Create a ZIP file containing the Excel file with the same username as the filename
    # with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    #     zipf.write(excel_filename, f'{username}.xlsx')

    print("created")
    return excel_filename, zip_filename
    

import io
import pandas as pd
import xlsxwriter
from datetime import datetime

def date_converter(date,formate):
    input_date = datetime.strptime(date, formate)
# Format the datetime object as MM-DD-YY
    output_date_str = input_date.strftime("%m-%d-%y")
    return output_date_str
# Format the datetime object as MM-DD-YY
# formatted_date = 
#

def create_database_contract_excel(data, username):
    # Create a dictionary to store rows for each sheet_type
    sheets_data = {}
    total_revenue_data = {'revenue': []}
    total_deferred_revenue_data = {'deffered_revenue': []}
    billing_data = {"billing": []}
    for i, entry in enumerate(data):
        print("hi hi hi hi hi hi hi ", i)
        sheet_type = entry.get('sheet_type')

        if sheet_type:
            if sheet_type not in sheets_data:
                sheets_data[sheet_type] = {'revenue': [], 'deffered_revenue': []}
            row = {'customer name': entry['items']['tansaction']['customer_name']}
            row['INVOICE DATE'] = date_converter(entry['items']['tansaction']['order_close_data'],"%Y-%m-%d")
            # row['INVOICE DATE'] = entry['items']['tansaction']['order_close_data']
            row['INVOICE NUMBER'] = entry['items']['tansaction']['invoice_number']
            row['Product/Service'] = entry['items']['productp_service']['product_name']
            row['Product/Type'] = entry['items']['productp_service']['productp_service_type']['productp_service_type']
            row['Qty'] = entry['items']['quantity']
            row['Sales Pric'] = entry['items']['sale_price']
            row['SUBSCRIPTION START DATE'] = date_converter(entry['items']['s_start_d'],"%Y-%m-%dT%H:%M:%SZ") if entry['items']['s_start_d'] else None
            row['SUBSCRIPTION END DATE'] = date_converter(entry['items']['s_end_d'],"%Y-%m-%dT%H:%M:%SZ")  if entry['items']['s_end_d'] else None
            
            for record in entry['revenue']:
                row[record['date']] = record['value']
            sheets_data[sheet_type]['revenue'].append(row)
            total_revenue_data['revenue'].append(row)


            # Add similar logic for 'revenue_type'
            row_type = {'customer name': entry['items']['tansaction']['customer_name']}
            row_type['INVOICE DATE'] = date_converter(entry['items']['tansaction']['order_close_data'],"%Y-%m-%d")
            # row_type['INVOICE DATE'] = entry['items']['tansaction']['order_close_data']
            row_type['INVOICE NUMBER'] = entry['items']['tansaction']['invoice_number']
            row_type['Product/Service'] = entry['items']['productp_service']['product_name']
            row_type['Product/Type'] = entry['items']['productp_service']['productp_service_type']['productp_service_type']
            row_type['Qty'] = entry['items']['quantity']
            row_type['Sales Pric'] = entry['items']['sale_price']
            row_type['SUBSCRIPTION START DATE'] =  date_converter(entry['items']['s_start_d'],"%Y-%m-%dT%H:%M:%SZ") if entry['items']['s_start_d'] else None
            row_type['SUBSCRIPTION END DATE'] = date_converter(entry['items']['s_end_d'],"%Y-%m-%dT%H:%M:%SZ")  if entry['items']['s_end_d'] else None

            for record in entry['deffered_revenue']:
                row_type[record['date']] = record['value']

            sheets_data[sheet_type]['deffered_revenue'].append(row_type)
            total_deferred_revenue_data['deffered_revenue'].append(row_type)


            # Add similar logic for 'billing'
            row_billing = {'customer name': entry['items']['tansaction']['customer_name']}
            row_billing['INVOICE DATE'] = date_converter(entry['items']['tansaction']['order_close_data'],"%Y-%m-%d")
            # row_billing['INVOICE DATE'] = entry['items']['tansaction']['order_close_data']
            row_billing['INVOICE NUMBER'] = entry['items']['tansaction']['invoice_number']
            row_billing['Product/Service'] = entry['items']['productp_service']['product_name']
            row_billing['Product/Type'] = entry['items']['productp_service']['productp_service_type']['productp_service_type']
            row_billing['Qty'] = entry['items']['quantity']
            row_billing['Sales Pric'] = entry['items']['sale_price']
            row_billing['SUBSCRIPTION START DATE'] =  date_converter(entry['items']['s_start_d'],"%Y-%m-%dT%H:%M:%SZ") if entry['items']['s_start_d'] else None
            row_billing['SUBSCRIPTION END DATE'] = date_converter(entry['items']['s_end_d'],"%Y-%m-%dT%H:%M:%SZ")  if entry['items']['s_end_d'] else None
            
            for record in entry['billing']:
                row_billing[record['date']] = record['value']
            
            billing_data['billing'].append(row_billing)




    # Create an in-memory Excel file
    excel_file = io.BytesIO()
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:

        # Create a worksheet for 'Billing'
        df_billing = pd.DataFrame(billing_data['billing'])

        # sorting coloums by date
        df_billing = sort_colums_by_date(df_billing)

        writer.sheets.setdefault('Billing',
                                 writer.book.add_worksheet('Billing'))
        worksheet = writer.sheets['Billing']
        worksheet.write(0, 0, 'Billing')

        df_billing.to_excel(writer, index=False, sheet_name='Billing',startrow=3)

        for sheet_type, sheet_data in sheets_data.items():
            # Create a worksheet for 'revenue'
            df_revenue = pd.DataFrame(sheet_data['revenue'])

            # sorting coloums by date
            df_revenue = sort_colums_by_date(df_revenue)

            # add by me
            # worksheet = writer.sheets[f'{sheet_type}_revenue']
            writer.sheets.setdefault(f'{sheet_type}_revenue',
                                     writer.book.add_worksheet(f'{sheet_type}_revenue'))
            worksheet = writer.sheets[f'{sheet_type}_revenue']
            worksheet.write(0, 0, f'{sheet_type}_revenue')
            # Write the custom text at the desired location (e.g., A1)
            # df_revenue.to_excel(writer, index=False, sheet_name=f'{sheet_type}_revenue')
            df_revenue.to_excel(writer, index=False, sheet_name=f'{sheet_type}_revenue',startrow=3)


            # Create a worksheet for 'revenue_type'
            df_revenue_type = pd.DataFrame(sheet_data['deffered_revenue'])

            # sorting coloums by date
            df_revenue_type = sort_colums_by_date(df_revenue_type)


            writer.sheets.setdefault(f'{sheet_type}_deferred_revenue',
                                     writer.book.add_worksheet(f'{sheet_type}_deferred_revenue'))
            worksheet = writer.sheets[f'{sheet_type}_deferred_revenue']
            worksheet.write(0, 0, f'{sheet_type}_deferred_revenue')

            df_revenue_type.to_excel(writer, index=False, sheet_name=f'{sheet_type}_deferred_revenue',startrow=3)

            # total revenue and deffered_revenue
        # Create a worksheet for 'Total Revenue'
        df_total_revenue = pd.DataFrame(total_revenue_data['revenue'])

        # sorting coloums by date
        df_total_revenue = sort_colums_by_date(df_total_revenue)

        writer.sheets.setdefault('Total_Revenue',
                                 writer.book.add_worksheet('Total_Revenue'))
        worksheet = writer.sheets['Total_Revenue']
        worksheet.write(0, 0, 'Total_Revenue')

        df_total_revenue.to_excel(writer, index=False, sheet_name='Total_Revenue',startrow=3)

        # Create a worksheet for 'Total Deferred Revenue'
        df_total_deferred_revenue = pd.DataFrame(total_deferred_revenue_data['deffered_revenue'])

        # sorting coloums by date
        df_total_deferred_revenue = sort_colums_by_date(df_total_deferred_revenue)

        writer.sheets.setdefault('Total_Deferred_Revenue',
                                 writer.book.add_worksheet('Total_Deferred_Revenue'))
        worksheet = writer.sheets['Total_Deferred_Revenue']
        worksheet.write(0, 0, 'Total_Deferred_Revenue')

        df_total_deferred_revenue.to_excel(writer, index=False, sheet_name='Total_Deferred_Revenue',startrow=3)


    # Seek back to the beginning of the stream
    excel_file.seek(0)

    excel_filename = f'{username}.xlsx'
    zip_filename = f'{username}.zip'

    # Save the Excel file with the username as the filename
    with open(excel_filename, 'wb') as file:
        file.write(excel_file.read())

    # # Create a ZIP file containing the Excel file with the same username as the filename
    # with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    #     zipf.write(excel_filename, f'{username}.xlsx')

    print("created")
    return excel_filename, zip_filename



import zipfile
import os

def create_database_contract_csv(data, field, username):

    # Create a list of dictionaries for each customer's data
    rows = []
    for entry in data:
        row = {'customer name': entry['items']['tansaction']['customer_name']}
        row['INVOICE DATE'] = date_converter(entry['items']['tansaction']['order_close_data'],"%Y-%m-%d")
        row['INVOICE NUMBER'] = entry['items']['tansaction']['invoice_number']
        row['Product/Service'] = entry['items']['productp_service']['product_name']
        row['Qty'] = entry['items']['quantity']
        row['Sales Pric'] = entry['items']['sale_price']
        row['SUBSCRIPTION START DATE'] = date_converter(entry['items']['s_start_d'], "%Y-%m-%dT%H:%M:%SZ") if \
        entry['items']['s_start_d'] else None
        row['SUBSCRIPTION END DATE'] = date_converter(entry['items']['s_end_d'], "%Y-%m-%dT%H:%M:%SZ") if \
        entry['items']['s_end_d'] else None

        for record in entry[field]:
            row[record['date']] = record['value']
        rows.append(row)

    df = pd.DataFrame(rows)
    df.columns = df.columns.str.replace(' ', '_')

    df = df.applymap(lambda x: f'"{x}"' if isinstance(x, str) and ' ' in x else x)

     # Save the DataFrame to a CSV file
    csv_filename = f'{username}.csv'
    df.to_csv(csv_filename, index=False)

    # Create a ZIP file containing the CSV file
    # zip_file_path = csv_filename.replace('.csv', '.zip')
    # with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    #     zipf.write(csv_filename, os.path.basename(csv_filename))

    # Return the paths of the generated CSV and ZIP files
    return csv_filename


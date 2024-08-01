import pandas as pd
import io


def Create_csv(data):

    # Create a list of dictionaries for each customer's data
    rows = []
    print(data,'===========-------=-=-=-=-+_+_+_==============')
    for entry in data:
        row = {
            'Product name': entry['product_name'],
            'Revenue Recognition': entry['productp_service_type']['productp_service_type'],
            'Revenue Type': entry['revenue_type']['revenue_type'],
        }
        rows.append(row)
        
    df = pd.DataFrame(rows)

    file = df.to_csv(index=False)
    return file


def Create_xslx(data):

    # Create a list of dictionaries for each customer's data
    rows = []
    print(data, "=-=-=-=-------------------------------------------")
    for entry in data:
        row = {
            'Product name': entry['product_name'],
            'Revenue Recognition': entry['productp_service_type']['productp_service_type'],
            'Revenue Type': entry['revenue_type']['revenue_type'],
        }
        rows.append(row)
        
    df = pd.DataFrame(rows)
    
    # Create an in-memory Excel file
    excel_file = io.BytesIO()
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    
    # Seek back to the beginning of the stream
    excel_file.seek(0)
    
    return excel_file


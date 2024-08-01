from services.models import ProductService
import json

def retrieve_product_data(data, user):
    data = json.loads(data)
    product_info = []
    products = data["QueryResponse"]["Item"]
    
    for item in products:
        if not ProductService.objects.filter(product_name = item["Name"]).exists():
            product_info.append(
                    ProductService(
                    product_name = item["Name"],
                    is_active = False,
                    user = user
                    )
            )
    ProductService.objects.bulk_create(product_info)
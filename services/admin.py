from django.contrib import admin
from.models import RevenueType, ProductServiceType, ProductService, ExpectedMonths

# Register your models here.

admin.site.register(RevenueType)
admin.site.register(ProductServiceType)
admin.site.register(ProductService)
admin.site.register(ExpectedMonths)

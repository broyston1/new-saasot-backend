from django.contrib import admin
from.models import(
    Item,
    Transaction,
    Calculation,
    CloseDate,
    CalculationMonths,
    ArrGracePeriod
)

# Register your models here.

admin.site.register(Item)
admin.site.register(Transaction)
admin.site.register(Calculation)
admin.site.register(CloseDate)
admin.site.register(CalculationMonths)
admin.site.register(ArrGracePeriod)
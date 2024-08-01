from rest_framework import permissions
from invoice.models import Transaction
from services.models import ProductService

from django.db.models import Q

class IsOwner(permissions.BasePermission):
    message = (
        "You do not have permission to update or delete."
    )

    def has_object_permission(self, request, view, obj):
        # Allow superusers to update or delete
        if request.user.is_superuser:
            return True
        # Allow users with role 1 to update or delete
        elif hasattr(request.user, 'role') and request.user.role == 1:
            return True
        # Allow object owner to update or delete
        return obj.user == request.user
    
    # def has_object_permission(self, request, view, obj):
    #     if request.user.is_superuser:
    #         return True

    #     return obj.user == request.user
    

class DuplicateInvoice(permissions.BasePermission):
    message = (
        "transaction of this invoice_number already exist"
    )

    def has_permission(self, request, view):
        data = request.data
        invoice_num = data['invoice_number']
        trans_id = data['transaction_id']
        if Transaction.objects.filter(Q(user__company = request.user.company, invoice_number = invoice_num ) | Q(user__company = request.user.company, transaction_id = trans_id)).exists():
            return False
        else:
            return True 


class DuplicatePriductService(permissions.BasePermission):
    message = (
        "ProductService of this product_name already exist"
    )

    def has_permission(self, request, view):
        data = request.data
        product_nam = data['product_name']
        if ProductService.objects.filter(user__company = request.user.company, product_name = product_nam ).exists():
            return False
        else:
            return True 


# -----for check value----
# class DuplicatePriductService(permissions.BasePermission):
#     message = (
#         "ProductService of this product_name already exist"
#     )

#     def has_permission(self, request, view):
#         data = request.data
#         product_nam = data['product_name']
#         if ProductService.objects.filter(user = request.user, product_name = product_nam ).exists():
#             return False
#         else:
#             return True 

class CalculationWrite(permissions.BasePermission):
    message = (
        "You do not have permission to update or check your password"
    )

    def has_permission(self, request, view):
        if request.user.role == 0 or request.user.role == 1:
            data = request.data 
            password = data['password']
            user = request.user
            if not user.check_password(password):
                return False
            else:
                return True
        else:
            return False 

    def has_object_permission(self, request, view, obj):
        if request.user.company == obj.items.tansaction.user.company:
            return True
        else:
            False

class IsAdmin(permissions.BasePermission):
    message = (
        "You do not have permission."
    )
    
    def has_permission(self, request, view):
        user = request.user

        return user.role in [1, 4]

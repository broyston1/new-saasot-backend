from authentication.models import CustomUser, Company
from rest_framework import serializers
from invoice.models import Transaction,Item
from invoice.saasot_calculation.revenue1 import* 
from invoice.saasot_calculation import revenue_month



class RegisterGetSerializer(serializers.ModelSerializer):

     class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name',
                  'email', 'role', 'company')
        




# class ArrByidCustomerSeriliazer(serializers.ModelSerializer):
#     arr = serializers.SerializerMethodField()
#     ids = serializers.SerializerMethodField()   

#     class Meta:
#         model = Transaction
#         fields = ["customer_name", "arr", "ids"]

#     def get_arr(self, obj):
#         context_data = self.context
#         calc_type = context_data.get('type')
#         user_id = context_data.get('user_id')
#         print("ffffffffffffffffffffffffffff",user_id)
#         items = Item.objects.filter(tansaction__user_id=user_id, tansaction__customer_name=obj.customer_name)
#         if calc_type == 'day':
#             return total_arr(items)
#         else:
#             return revenue_month.total_arr(items)

#     def get_ids(self, obj):
#         ids = []
#         context_data = self.context
#         user_id = context_data.get('user_id')
#         transactions = Transaction.objects.filter(user_id=user_id, customer_name=obj.customer_name)
#         for transaction in transactions:
#             ids.append(transaction.id)
#         return ids
    










class ArrByCustomerIdSeriliazer(serializers.ModelSerializer):
    # customer_name = serializers.CharField(source = "customer_name")
    arr = serializers.SerializerMethodField()
    ids = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ["customer_name", "arr", "ids"]

    def get_arr(self, obj):
        context_data = self.context
        calc_type = context_data.get('type')
        company_id = context_data.get('company_id')
        customer_name = ''


        # print('vijay')
        # print(company_id)
        # print(customer_name)


        items = Item.objects.filter(tansaction__user__company__id=company_id,tansaction__customer_name=obj.customer_name)

        # print(items)
      
        if calc_type == 'day':
            return total_arr(items)
        else:
            return revenue_month.total_arr(items)

    def get_ids(self, obj):
        ids = []
        context_data = self.context
        company_id = context_data.get('company_id')
        transaction = Transaction.objects.filter(user__company__id=company_id, customer_name=obj.customer_name)
        for tsc in transaction:
            ids.append(tsc.id)
        return ids
    






class PendingArrIDCustomerSeriliazer(serializers.ModelSerializer):
    # customer_name = serializers.CharField(source = "customer_name")
    arr = serializers.SerializerMethodField()
    ids = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ["customer_name", "arr", "ids"]

    def get_arr(self, obj):
        context_data = self.context
        calc_type = context_data.get('type')
        company_id = context_data.get('company_id')
        items = Item.objects.filter(tansaction__user__company__id=company_id,tansaction__customer_name=obj.customer_name)
        if calc_type == 'day':
            return total_pending_arr(items)
        else:
            return revenue_month.total_pending_arr(items)

    def get_ids(self, obj):
        ids = []
        context_data = self.context
        company_id = context_data.get('company_id')
        transaction = Transaction.objects.filter(user__company__id=company_id, customer_name=obj.customer_name)
        for tsc in transaction:
            ids.append(tsc.id)
        return ids
    

class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = '__all__'


























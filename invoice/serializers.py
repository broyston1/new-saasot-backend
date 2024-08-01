import calendar
from itertools import product

from rest_framework import serializers
from .models import Transaction, Item, Calculation, CloseDate, CalculationMonths, ArrGracePeriod
from dateutil.relativedelta import relativedelta
from datetime import datetime
from .saasot_calculation.revenue1 import* 
from .saasot_calculation import revenue_month
from services.serializers import ProductServiceTypeSerializer, RevenueTypeSerializer
from services.models import ProductService
from authentication.models import Company


class UploadCsvSerializer(serializers.Serializer):
    csv_file = serializers.FileField(required=True)

    # def validate_csv_file(self, value):
    #     if not hasattr(value, 'read'):
    #         raise serializers.ValidationError("Please provide a valid CSV file.")

    #     return value


class CreateItemListSerializer(serializers.ModelSerializer):
    ...

    class Meta:
        model = Item
        fields = '__all__'
        depth = 2


class ItemListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        item_mapping = {item.id: item for item in instance}

        result = []
        for item_data in validated_data:
            item_id = item_data.get('id', None)
            if item_id is not None and item_id in item_mapping:
                item_instance = item_mapping[item_id]
                self.child.update(item_instance, item_data)
                result.append(item_instance)
            else:
                result.append(self.child.create(item_data))

        # Delete items that were not included in the update
        item_ids = [item_data.get('id', None) for item_data in validated_data]
        for item in instance:
            if item.id not in item_ids:
                item.delete()

        return result


class ItemSerializer(serializers.ModelSerializer):
    ...

    class Meta:
        model = Item
        fields = '__all__'
        list_serializer_class = ItemListSerializer

    def validate(self, data):
        """
        Check that the start or end_date is assign if product service revenue type is over life of subscription.
        """
        product_service = data['productp_service']
        if product_service.revenue_type == None:
            raise serializers.ValidationError({"indefined_product_service": "please defined the product service"})
        if product_service.revenue_type.revenue_type == "over life of subscription":
            if data['s_start_d'] is None or data['s_end_d'] is None:
                raise serializers.ValidationError({"invalid_date": "please select the start or end date"})
        return data
    

class CreateTransactionSerliazer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = '__all__'


class UpdateTransactionSerliazer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['invoice_number', 'transaction_id']


class DynamicFieldsModelSerializer(serializers.Serializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            not_allowed = set(fields)
            existing = set(self.fields)
            for field_name in not_allowed:
                self.fields.pop(field_name)


class ItemRevenueSeriliazer(DynamicFieldsModelSerializer):
    revenue = serializers.SerializerMethodField()
    billing = serializers.SerializerMethodField()
    deffered_revenue = serializers.SerializerMethodField()
    # heading = serializers.SerializerMethodField(source='get_heading', read_only=True)

    class Meta:
        model = Item
        fields = '__all__'
        depth = 1

    def get_calculation(self, obj):
        context_data = self.context
        calc_type = context_data.get('type')
        if calc_type == 'day':
            return obj.items
        else:
            return obj.item

    def get_revenue(self, obj):
        calc = self.get_calculation(obj)
        return calc.revenue if calc else None

    def get_billing(self, obj):
        calc = self.get_calculation(obj)
        return calc.billing if calc else None

    def get_deffered_revenue(self, obj):
        calc = self.get_calculation(obj)
        return calc.deffered_revenue if calc else None

class ItemCalcSerilizer(serializers.ModelSerializer):
    revenue = serializers.SerializerMethodField()
    deffered_revenue = serializers.SerializerMethodField()
    billing = serializers.SerializerMethodField()

    item_arr = serializers.SerializerMethodField()

    tansaction = serializers.PrimaryKeyRelatedField(read_only=True)
    heading = ProductServiceTypeSerializer(source='productp_service.productp_service_type')
    revenue_type = serializers.CharField(source = "productp_service.revenue_type")
    product_service_name = serializers.CharField(source='productp_service.product_name', read_only=True)
    product_service_id = serializers.CharField(source='productp_service.id', read_only=True)

    
    class Meta:
        model = Item
        fields = '__all__'
        depth = 1

    def get_revenue(self, obj):
        context_data = self.context
        calc_type = context_data.get('type')
        try:
            close_date = CloseDate.objects.all().first()
            close_date = close_date.close_date
            rev_list = []
            if calc_type == 'day':
                calc = Calculation.objects.get(items = obj)
                for item in calc.revenue:
                    revenue = {}
                    revenue['date'] = item['date']
                    revenue['value'] = item['value']
                    revenue['update'] = item['update']
                    if datetime.strptime(item['date'], "%b %y").date() <= close_date.date():
                        revenue['status'] = 'red'
                    else:
                        revenue['status'] = 'black'
                    rev_list.append(revenue)
                return {"id": calc.id, "revenue": rev_list}
            else:
                calc = CalculationMonths.objects.get(items = obj)
                for item in calc.revenue:
                    revenue = {}
                    revenue['date'] = item['date']
                    revenue['value'] = item['value']
                    revenue['update'] = item['update']
                    if datetime.strptime(item['date'], "%b %y").date() <= close_date.date():
                        revenue['status'] = 'red'
                    else:
                        revenue['status'] = 'black'
                    rev_list.append(revenue)
                return {"id": calc.id, "revenue": rev_list}
        except:
            if calc_type == 'day':
                calc = Calculation.objects.get(items = obj)
                return {"id": calc.id, "revenue": calc.revenue}
            else:
                calc = CalculationMonths.objects.get(items = obj)
                return {"id": calc.id, "revenue": calc.revenue}
            

    def get_billing(self, obj):
        context_data = self.context
        calc_type = context_data.get('type')

        if calc_type == 'day':
            calc = Calculation.objects.get(items = obj)
            return {"id": calc.id, "billing": calc.billing}
        else:
            calc = CalculationMonths.objects.get(items = obj)
            return {"id": calc.id, "billing": calc.billing}

    def get_deffered_revenue(self, obj):
        context_data = self.context
        calc_type = context_data.get('type')

        if calc_type == 'day':
            calc = Calculation.objects.get(items = obj)
            return {"id": calc.id, "deffered_revenue": calc.deffered_revenue}
        else:
            calc = CalculationMonths.objects.get(items = obj)
            return {"id": calc.id, "deffered_revenue": calc.deffered_revenue}
    
    def get_item_arr(self, obj):
        context_data = self.context
        calc_type = context_data.get('type')
        if calc_type == 'day':
            calc = Calculation.objects.get(items = obj)
            return {"id": calc.id, "arr": calc.arr}
        else:
            calc = CalculationMonths.objects.get(items = obj)
            return {"id": calc.id, "arr": calc.arr}


class TransactionScreenSerilizer(serializers.ModelSerializer):
    # arr = serializers.SerializerMethodField()
    add_on = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    class Meta:
        model = Transaction
        fields = '__all__'

    # def get_arr(self, obj):
    #     items = Item.objects.filter(tansaction=obj)
    #     return total_arr(items)
        
    def get_items(self, obj):
        context_data = self.context
        calc_type = context_data.get('type')
        items = Item.objects.filter(tansaction__id=obj.id)
        # print('vijay6')
        # print(items)
        return ItemCalcSerilizer(items, many=True, context={'type': calc_type}).data
    
    def get_add_on(self, obj):
        context_data = self.context
        calc_type = context_data.get('type')
        items = Item.objects.filter(tansaction__id=obj.id)
        items_seriliaze = ItemCalcSerilizer(items, many=True, context={'type': calc_type}).data

        dictt = {}
        list_dict = []
        added_type = []
        for i in range(0, len(items_seriliaze)):
            if len(items_seriliaze)>0:
                if items_seriliaze[i]['heading']['productp_service_type'] in added_type:
                    continue
                list_dict.append(items_seriliaze[i])
                for k in range(0, len(items_seriliaze)):
                    if i!=k:
                        if items_seriliaze[i]['heading']['productp_service_type']==items_seriliaze[k]['heading']['productp_service_type']:
                            list_dict.append(items_seriliaze[k])
                        # else:
                        #     list_dict.append(items_seriliaze[i])
                dictt[items_seriliaze[i]['heading']['productp_service_type']]=list_dict
                list_dict = []
                added_type.append(items_seriliaze[i]['heading']['productp_service_type'])
 
        return dictt


class ArrByCustomerSeriliazer(serializers.ModelSerializer):
    # customer_name = serializers.CharField(source = "customer_name")
    arr = serializers.SerializerMethodField()
    ids = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ["customer_name", "arr", "ids"]

    def get_arr(self, obj):
        context_data = self.context
        calc_type = context_data.get('type')
        user = context_data.get('user')
        items = Item.objects.filter(tansaction__user__company=user.company,tansaction__customer_name=obj.customer_name)
        if calc_type == 'day':
            return total_arr(items)
        else:
            return revenue_month.total_arr(items)

    def get_ids(self, obj):
        ids = []
        context_data = self.context
        user = context_data.get('user')
        transaction = Transaction.objects.filter(user__company=user.company, customer_name=obj.customer_name)
        for tsc in transaction:
            ids.append(tsc.id)
        return ids

class CreateCalculationSeriliazer(serializers.ModelSerializer):
    
    class Meta:
        model = Calculation
        fields = '__all__'

class CloseDateSeriliazer(serializers.ModelSerializer):

    class Meta:
        model = CloseDate
        fields = '__all__'

class ArrGracePeriodSerializer(serializers.ModelSerializer):

    class Meta:
        model = ArrGracePeriod
        fields = '__all__'

# class ArrGracePeriodSerializer(serializers.Serializer):
#     months = serializers.IntegerField(default=0)
#     company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), allow_null=False, allow_empty=False)


# class CalculationDay(DynamicFieldsModelSerializer):
#     items = CreateItemListSerializer()
#     class Meta:
#         model = Calculation
#         fields = ('revenue', 'billing', 'deffered_revenue', 'items')
#         # depth = 1

class CalculationDaySerializer(DynamicFieldsModelSerializer):
    items = CreateItemListSerializer(read_only=True)  # Assuming CreateItemListSerializer is your read-only serializer

    revenue = serializers.ListSerializer(child=serializers.DictField(), read_only=True)
    billing = serializers.ListSerializer(child=serializers.DictField(), read_only=True)
    deffered_revenue =  serializers.ListSerializer(child=serializers.DictField(), read_only=True)
    sheet_type = serializers.SerializerMethodField()


    def get_sheet_type(self, obj):
        if obj:
          return obj.items.productp_service.productp_service_type.productp_service_type
    # productp_service = serializers.CharField(source='items.productp_service.product_name', read_only=True)
    # customer_name = serializers.CharField(source = "items.tansaction.customer_name" , read_only=True)
    # invoice_number = serializers.CharField(source = "items.tansaction.invoice_number", read_only=True)
    # invoice_date = serializers.CharField(source = "items.tansaction.order_close_data", read_only=True)
    # quantity = serializers.CharField(source = "items.quantity", read_only=True)
    # sale_price = serializers.CharField(source = "items.sale_price", read_only=True)
    # amount = serializers.CharField(source = "items.amount", read_only=True)
    # s_start_d = serializers.CharField(source = "items.s_start_d", read_only=True)
    # s_end_d = serializers.CharField(source = "items.s_end_d", read_only=True)

class CalculationMonth(DynamicFieldsModelSerializer):
    items = CreateItemListSerializer()

    class Meta:
        model = CalculationMonths
        fields = ('revenue', 'billing', 'deffered_revenue', 'items','sheet_type')
        depth = 1



class PendingArrByCustomerSeriliazer(serializers.ModelSerializer):
    # customer_name = serializers.CharField(source = "customer_name")
    arr = serializers.SerializerMethodField()
    ids = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ["customer_name", "arr", "ids"]

    def get_arr(self, obj):
        context_data = self.context
        calc_type = context_data.get('type')
        user = context_data.get('user')
        items = Item.objects.filter(tansaction__user__company=user.company,tansaction__customer_name=obj.customer_name)
        if calc_type == 'day':
            return total_pending_arr(items)
        else:
            return revenue_month.total_pending_arr(items)

    def get_ids(self, obj):
        ids = []
        context_data = self.context
        user = context_data.get('user')
        transaction = Transaction.objects.filter(user__company=user.company, customer_name=obj.customer_name)
        for tsc in transaction:
            ids.append(tsc.id)
        return ids
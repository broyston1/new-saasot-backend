from django.shortcuts import render
from rest_framework import generics
from authentication.models import CustomUser
from .serializers import RegisterGetSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from services.models import ProductServiceType
from django.shortcuts import get_object_or_404
from rest_framework import viewsets

# from .models import Transaction, Item
# from invoice.saasot_calculation import total_calc2
from invoice.saasot_calculation.total_calc2 import parse_date
from invoice.pagination import CustomPagination
from invoice.filters import StartsWithSearchFilter
from django.db.models import F, Q
from django.db.models import Subquery
from django.core.cache import cache
from invoice.saasot_calculation import total_calc2
from dateutil.relativedelta import relativedelta
from invoice.serializers import (ArrByCustomerSeriliazer,PendingArrByCustomerSeriliazer,CalculationDaySerializer,ArrByCustomerSeriliazer,UploadCsvSerializer,CreateItemListSerializer,TransactionScreenSerilizer)
from invoice.models import Transaction, Item,Calculation,CalculationMonths,Company
from .serializers import ArrByCustomerIdSeriliazer,PendingArrIDCustomerSeriliazer, CompanySerializer
# Create your views here.


class UserListView(generics.ListAPIView):
    serializer_class = RegisterGetSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(role=CustomUser.USER)
    


from dateutil.relativedelta import relativedelta

# class StartEndPeriod(APIView):
#     # permission_classes = [IsAuthenticated]


#     def get(self, request, user_id, *args, **kwargs):

#         try:
#             user = CustomUser.objects.get(id=user_id)
#         except CustomUser.DoesNotExist:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

#         data = {
#             "user_id": user_id,
#             "starting_period": [],
#             "ending_period": []
#         }

#         starting_period = data["starting_period"]
#         start_p = parse_date("Jan 16")
#         start_p_end = parse_date("Nov 29")
#         current_date = start_p
#         while current_date <= start_p_end:
#             starting_period.append(current_date.strftime("%b %y"))
#             current_date += relativedelta(months=1)

#         ending_period = data["ending_period"]
#         start_p = parse_date("Jan 16")
#         start_p_end = parse_date("Nov 29")
#         current_date = start_p
#         while current_date <= start_p_end:
#             ending_period.append(current_date.strftime("%b %y"))
#             current_date += relativedelta(months=1)

#         return Response(data, status=status.HTTP_200_OK)
    




class ItemRevenueView(generics.ListAPIView):
    """
    A viewset that calculates the revenue and other things on an item-based.
    """
    serializer_class = CalculationDaySerializer
    # permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [StartsWithSearchFilter]
    search_fields = ['items__transaction__customer_name']

    def get_ordering(self):
        ordering = self.request.query_params.get('ordering')
        return ordering
    

    def get_queryset(self, *args, **kwargs):
        
        user_id = self.kwargs.get('user_id')  # Get user ID from URL
        company_id = self.kwargs.get('company_id')
        # user = get_object_or_404(CustomUser, id=user_id)  # Assuming User is your user model
        company = get_object_or_404(Company, id=company_id)
        # new_id = user.id
        queryset = Calculation.objects.filter(
            # items__tansaction__user_id=new_id,
            items__tansaction__user_id__company=company)
        

        if self.kwargs.get('typ') != 'day':
            queryset = CalculationMonths.objects.filter(
                    # items__tansaction__user_id=new_id,
                    items__tansaction__user_id__company=company)

        queryset = self.filter_queryset(queryset)

        query = self.kwargs.get('query')
        query_list = query.split(' ')

        if "billing" in query or 'total' in query:
            pass
        else:
            queryset = queryset.filter(
                items__transaction__user=company,
                items__productp_service__productp_service_type__productp_service_type=query_list[0]
            ).order_by('items__s_start_d')

        ordering = self.get_ordering()
        if ordering:
            queryset = queryset.order_by(ordering)

        return_fields = ['revenue', 'billing', 'deffered_revenue']
        if "deferred" in query:
            return_fields.remove('deffered_revenue')
        elif "billing" in query:
            return_fields.remove('billing')
        else:
            return_fields.remove('revenue')

        self.return_fields = return_fields
        return queryset

    def list(self, request, *args, **kwargs):
        start = parse_date(self.kwargs.get('start'))
        end = parse_date(self.kwargs.get('end'))
        current_date = start
        heading = []

        while current_date <= end:
            heading.append(current_date.strftime("%b %y"))
            current_date += relativedelta(months=1)

        queryset = self.filter_queryset(self.get_queryset())

        if self.request.GET.get('page'):
            paginated_data = self.paginate_queryset(queryset)

            serializer = CalculationDaySerializer(
                paginated_data, many=True, fields=self.return_fields)

            page_size = self.paginator.page.paginator.count // 20
            if self.paginator.page.paginator.count % 20 == 0:
                page_size = page_size-1
            else:
                page_size = page_size+1

            response_data = {
                "links": {
                    "next": self.paginator.get_next_link(),
                    "previous": self.paginator.get_previous_link()
                },
                "page_size": page_size,
                "count": self.paginator.page.paginator.count,
                "data": serializer.data,
                "heading": heading
            }
            return Response(response_data, status=status.HTTP_200_OK)

        else:
            serializer = CalculationDaySerializer(
                queryset, many=True, fields=self.return_fields)

        return Response({"data": serializer.data, "heading": heading}), 


class DatabaseDropdownList(APIView):

    def get(self, request, *args, **kwargs):
        new_list = []
        
        # Retrieve user ID from the request object
        company_id = self.kwargs.get('user_id')
        
        # Modify the query to filter based on user ID
        prd_types = ProductServiceType.objects.filter(
            user__company__id=company_id)
        
        for prd in prd_types:
            new_list.append(
                {"name": str(prd.productp_service_type) + " revenue", "id": prd.id})
            new_list.append(
                {"name": str(prd.productp_service_type) + " deferred revenue", "id": prd.id})
        
        new_list.append({"name": "billing"})
        new_list.append({"name": "total revenue"})
        new_list.append({"name": "total deferred revenue"})
        
        return Response({"data": new_list}, status=status.HTTP_200_OK)
    
    

# class PendingArr(APIView):

#     serializer_class = ArrByidCustomerSeriliazer
#     # permission_classes = [IsAuthenticated]

#     @staticmethod
#     def get_user_id_from_url(request):
#         # Extract user ID from the URL
#         user_id = request.parser_context['kwargs'].get('user_id')
#         return user_id

#     def get_queryset(self, user_id):
#         item_ids = Item.objects.filter(
#             Q(total_revenue__isnull=False) | Q(total_revenue__gt=0),
#             tansaction__user__company=user_id,  # Filter by user ID from URL
#             productp_service__revenue_type__revenue_type="over life of subscription"
#         ).values('tansaction_id')

#         return Transaction.objects.filter(
#             id__in=Subquery(item_ids), user_id=user_id
#         ).order_by('customer_name').distinct('customer_name')

#     def get(self, request, *args, **kwargs):
#         user_id = self.get_user_id_from_url(request)

#         cache_key = f"user_{user_id}_pending_arr"

#         cached_data = cache.get(cache_key)

#         if cached_data:
#             return Response(cached_data)

#         queryset = self.get_queryset(user_id)
#         calc_type = self.kwargs.get('typ')
#         serializer = ArrByidCustomerSeriliazer(
#             queryset, many=True, context={'type': calc_type, "user": user_id})
        
#         heading = []
#         start = self.kwargs.get('start')
#         start = parse_date(start)
#         end = self.kwargs.get('end')
#         end = parse_date(end)
#         current_date = start
#         while current_date <= end:
#             heading.append(current_date.strftime("%b %y"))
#             current_date += relativedelta(months=1)

#         data = total_calc2.peding_arr(serializer.data)
#         data = {"heading": heading, "data": data}
#         cache.set(cache_key, data, timeout=3600)

#         return Response(data)








class PendingArr(APIView):

    serializer_class = ArrByCustomerIdSeriliazer

    def get_queryset(self, *args, **kwargs):
        company_id = self.kwargs.get('company_id')
        
        item_ids = Item.objects.filter(
            Q(total_revenue__isnull=False) | Q(total_revenue__gt=0),
            tansaction__user__company_id=company_id,
            productp_service__revenue_type__revenue_type="over life of subscription"
        ).values('tansaction_id')
        # Retrieve unique transactions with transaction IDs from the above subquery
        return Transaction.objects.filter(
            id__in=Subquery(item_ids), user__company__id=company_id
        ).order_by('customer_name').distinct('customer_name')

    def get(self, request, *args, **kwargs):

        company_id = self.kwargs.get('company_id')

        # user = request.user
        
        cache_key = f"user_company__id{company_id}_pending_arr"

        # Check if the response is cached for this user.
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset()
        calc_type = self.kwargs.get('typ')
        company_id = self.kwargs.get('company_id')

        serializer = PendingArrIDCustomerSeriliazer(
            queryset, many=True, context={'type': calc_type, "company_id": company_id})

        heading = []
        # start = Item.objects.earliest('s_start_d').s_start_d
        # end = Item.objects.exclude(s_end_d=None).order_by('-s_end_d').first().s_end_d
        # current_date = start
        start = self.kwargs.get('start')
        start = parse_date(start)
        end = self.kwargs.get('end')
        end = parse_date(end)
        current_date = start
        while current_date <= end:
            heading.append(current_date.strftime("%b %y"))
            current_date += relativedelta(months=1)

        data = total_calc2.peding_arr(serializer.data)
        data = {"heading": heading, "data": data}
        cache.set(cache_key, data, timeout=3600)

        return Response(data)
    


class TableTotal(APIView):

    def get_queryset(self, *args, **kwargs):
        company_id = self.kwargs.get('company_id')
        queryset = Calculation.objects.filter(
            items__tansaction__user__company=company_id)
        if self.kwargs.get('typ') != 'day':
            queryset = CalculationMonths.objects.filter(
                items__tansaction__user__company=company_id)

        query = self.kwargs.get('query')
        query_list = query.split(' ')

        if "billing" in query or 'total' in query or 'arr' in query:
            pass

        else:
            queryset = queryset.filter(items__tansaction__user__company=company_id,
                                       items__productp_service__productp_service_type__productp_service_type=query_list[0]
                                       )

        return queryset.order_by('items__tansaction')

    def get(self, request, *args, **kwargs):

        queryset = self.get_queryset()
        query = self.kwargs.get('query')

        # total of all caculation according to date
        total = []
        for calc in queryset:
            if "deferred" in query:
                calc_data = calc.deffered_revenue
            elif "billing" in query:
                calc_data = calc.billing
            elif "arr" in query:
                calc_data = calc.arr
            else:
                calc_data = calc.revenue
            combined = {}

    # -------------------- calculate total_revenue--------------------
            for item in total:
                combined[item['date']] = combined.get(
                    item['date'], 0) + item['value']

            if calc_data != None:
                for item in calc_data:
                    combined[item['date']] = combined.get(
                        item['date'], 0) + item['value']

            total = [{"date": date, "value": value}
                     for date, value in combined.items()]
        try:
            # Add missing month with 0 value
            all_dates = set(item['date'] for item in total)
            min_date = min(all_dates, key=parse_date)
            max_date = max(all_dates, key=parse_date)
            all_dates_with_zero = set(
                (parse_date(min_date) + timedelta(days=30*i)).strftime("%b %y")
                for i in range((parse_date(max_date) - parse_date(min_date)).days // 30 + 1)
            )
            missing_dates = all_dates_with_zero - all_dates
            total.extend([{"date": date, "value": 0}
                         for date in missing_dates])
        except:
            pass
        total.sort(key=lambda x: parse_date(x['date']))

        return Response({'total': total}, status=status.HTTP_200_OK)



class ArrRollForwardView(APIView):

    serializer_class = ArrByCustomerIdSeriliazer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        company_id = self.kwargs.get('company_id')

        item_ids = Item.objects.filter(
            Q(total_revenue__isnull=False) | Q(total_revenue__gt=0),
            tansaction__user__company__id=company_id,
            productp_service__revenue_type__revenue_type="over life of subscription"
        ).values('tansaction_id')

        # Retrieve unique transactions with transaction IDs from the above subquery
        return Transaction.objects.filter(
            id__in=Subquery(item_ids), user__company__id=company_id
        ).order_by('customer_name').distinct('customer_name')

    def get(self, request, *args, **kwargs):
        company_id = self.kwargs.get('company_id')

        user = request.user
        cache_key = f"user_company__id{company_id}_data"

        # Check if the response is cached for this user.
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset()
        calc_type = self.kwargs.get('typ')
        company_id = self.kwargs.get('company_id')
        serializer = ArrByCustomerIdSeriliazer(queryset, many=True, context={
                                             'type': calc_type, "company_id": company_id})

        heading = []
        # start = Item.objects.earliest('s_start_d').s_start_d
        # end = Item.objects.exclude(s_end_d=None).order_by('-s_end_d').first().s_end_d
        # current_date = start
        start = self.kwargs.get('start')
        start = parse_date(start)
        end = self.kwargs.get('end')
        end = parse_date(end)
        current_date = start
        while current_date <= end:
            heading.append(current_date.strftime("%b %y"))
            current_date += relativedelta(months=1)

        arr_roll_fwd = total_calc2.arr_rollforward(serializer.data)

        Logo_Rollforward = arr_roll_fwd['Logo_Rollforward']
        key_metcrics = arr_roll_fwd['key_metcrics']
        del arr_roll_fwd['key_metcrics']
        del arr_roll_fwd['Logo_Rollforward']
        side_heading = [
            "Beggining_ARR", "New_ARR", "Recovery_ARR", "Expansion_ARR",
            "Contraction_ARR", "Churn_ARR",
            "Ending_ARR"
        ]

        data = {"arr_roll_fwd": arr_roll_fwd, "heading": heading, "side_heading": side_heading,
                'Logo_Rollforward': Logo_Rollforward, "Key_Metcrics": key_metcrics}
        cache.set(cache_key, data, timeout=3600)

        return Response(data)
    

class ClearUserCacheView(APIView):

    def get(self, request, *args, **kwargs):
        # Construct a unique cache key for the user based on user_id
        # user = request.user
        company_id = self.kwargs.get('company_id')
        
        cache_key = f"user_company__id{company_id}_data"
        cached_data = cache.get(cache_key)
        cache_key2 = f"user_company__id{company_id}_pending_arr"

        # Delete the cache for the specific user
        cache.delete(cache_key)
        cache.delete(cache_key2)

        return Response({'message': f'Cache cleared for Company {company_id}'})





    






from rest_framework.filters import OrderingFilter




# class ArrByCustomerView(generics.ListAPIView):
#     """
#     A viewset that calculates the ARR of a customer based on the customer_name on transactions.
#     """
#     serializer_class = ArrByidCustomerSeriliazer
#     # permission_classes = [IsAuthenticated]
#     pagination_class = CustomPagination
#     filter_backends = [StartsWithSearchFilter, OrderingFilter]
#     search_fields = ['customer_name']
#     ordering_fields = ['customer_name']

#     def get_queryset(self, *args, **kwargs):
#         user_id = self.kwargs.get('user_id')  # Assuming user_id is passed as a URL parameter

#         # Filtering items based on the user's ID
#         item_ids = Item.objects.filter(
#             tansaction__user_id=user_id,  # Adjust this to match your model structure
#             productp_service__revenue_type__revenue_type="over life of subscription"  # Adjust this to match your model structure
#         ).values('tansaction_id')

#         # Fetching transactions based on the filtered item IDs
#         queryset = Transaction.objects.filter(
#             id__in=item_ids, user_id=user_id
#         ).distinct('customer_name')

#         # Check if there's a sorting parameter in the URL
#         ordering = self.request.query_params.get('ordering')
#         if ordering == '-customer_name':
#             # Order by customer_name in descending order
#             queryset = queryset.order_by(F('customer_name').desc())

#         return queryset

#     def list(self, request, *args, **kwargs):
#         user_id = self.kwargs.get('user_id')  # Assuming user_id is passed as a URL parameter

#         queryset = self.filter_queryset(self.get_queryset(user_id)).distinct('customer_name')
#         heading = []

#         start = self.kwargs.get('start')
#         start = parse_date(start)
#         end = self.kwargs.get('end')
#         end = parse_date(end)
#         current_date = start
#         while current_date <= end:
#             heading.append(current_date.strftime("%b %y"))
#             current_date += relativedelta(months=1)

#         calc_type = self.kwargs.get('typ')

#         if self.request.GET.get('page'):
#             paginated_data = self.paginate_queryset(queryset)

#             serializer = ArrByidCustomerSeriliazer(
#                 paginated_data, many=True,
#                 context={"type": calc_type, "user_id": user_id}
#             )

#             page_size = self.paginator.page.paginator.count // 20
#             if self.paginator.page.paginator.count % 20 == 0:
#                 page_size = page_size - 1
#             else:
#                 page_size = page_size + 1

#             response_data = {
#                 "links": {
#                     "next": self.paginator.get_next_link(),
#                     "previous": self.paginator.get_previous_link()
#                 },
#                 "page_size": page_size,
#                 "count": self.paginator.page.paginator.count,
#                 "data": serializer.data,
#                 "heading": heading
#             }
#             return Response(response_data, status=status.HTTP_200_OK)

#         else:
#             serializer = ArrByidCustomerSeriliazer(queryset, many=True, context={"type": calc_type, "user_id": user_id})

#         return Response({"data": serializer.data, "heading": heading})
    




class ArrByCustomerView(generics.ListAPIView):
    """
    A viewset that calculates the ARR of a customer based on the customer_name on transactions.
    """
    serializer_class = ArrByCustomerIdSeriliazer

    pagination_class = CustomPagination
    filter_backends = [StartsWithSearchFilter, OrderingFilter]
    search_fields = ['customer_name']
    ordering_fields = ['customer_name']

    def get_queryset(self, *args, **kwargs):
        company_id = self.kwargs.get('company_id')

        item_ids = Item.objects.filter(
            tansaction__user__company__id=company_id,
            productp_service__revenue_type__revenue_type="over life of subscription"
        ).values('tansaction_id')

        queryset = Transaction.objects.filter(
            id__in=item_ids, user__company__id=company_id
        ).distinct('customer_name')

        # Check if there's a sorting parameter in the URL
        ordering = self.request.query_params.get('ordering')
        if ordering == '-customer_name':
            # Order by customer_name in descending order
            queryset = queryset.order_by(F('customer_name').desc())

        return queryset

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset()).distinct('customer_name')
        heading = []

        start = self.kwargs.get('start')
        start = parse_date(start)
        end = self.kwargs.get('end')
        end = parse_date(end)
        current_date = start
        while current_date <= end:
            heading.append(current_date.strftime("%b %y"))
            current_date += relativedelta(months=1)

        calc_type = self.kwargs.get('typ')
        company_id = self.kwargs.get('company_id')

        if self.request.GET.get('page'):
            paginated_data = self.paginate_queryset(queryset)

            serializer = ArrByCustomerIdSeriliazer(
                paginated_data, many=True,
                context={"type": calc_type, "company_id": company_id}
            )

            page_size = self.paginator.page.paginator.count // 20
            if self.paginator.page.paginator.count % 20 == 0:
                page_size = page_size - 1
            else:
                page_size = page_size + 1

            response_data = {
                "links": {
                    "next": self.paginator.get_next_link(),
                    "previous": self.paginator.get_previous_link()
                },
                "page_size": page_size,
                "count": self.paginator.page.paginator.count,
                "data": serializer.data,
                "heading": heading
            }
            return Response(response_data, status=status.HTTP_200_OK)

        else:
            serializer = ArrByCustomerSeriliazer(queryset, many=True, context={"type": calc_type, "user": self.request.user})

        return Response({"data": serializer.data, "heading": heading})











from invoice.newret import load_membership_data



class UploadCsvView(APIView):
    """
    A viewset that provides the upload csv functionality 
    """
    serializer_class = UploadCsvSerializer
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        if 'csv_file' not in data.keys():
            return Response({"message": "'csv_file' key not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        if data['csv_file']:
            serializer = UploadCsvSerializer(data=data)
            if serializer.is_valid():
                # Retrieve the user ID
                user_id = request.user.id
                
                # Pass the user ID to the load_membership_data function
                undefiend_service = load_membership_data(data['csv_file'], user_id)
                
                if undefiend_service.get('error', None):
                    return Response({'message': str(undefiend_service['error'])}, status=status.HTTP_400_BAD_REQUEST)
                
                return Response({"undefiend_service": undefiend_service, "message": "Successfully uploaded"}, status=status.HTTP_200_OK)

            else:
                return Response({'message': 'There is an error in the data'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "File is required to send "}, status=status.HTTP_400_BAD_REQUEST)








# class ItemlistView(generics.ListAPIView):
#     """
#     A viewset that provides the list of items for a specific user
#     """
#     serializer_class = CreateItemListSerializer
#     # permission_classes = [IsAuthenticated]
#     pagination_class = CustomPagination
#     filter_backends = [StartsWithSearchFilter]
#     search_fields = ['tansaction__customer_name']

#     def get_user_id(self):
#         # Assuming you're passing user_id as a query parameter in the request
#         return self.request.query_params.get('user_id', None)

#     def get_queryset(self):
#         user_id = self.get_user_id()
#         user = get_object_or_404(CustomUser, id=user_id)

#         items = Item.objects.filter(tansaction__user__id=user.id).annotate(
#             redflag=F('tansaction__red_flag')
#         )

#         return items.order_by('-redflag', 'tansaction')

#     def list(self, request):
#         user_id = self.get_user_id()

#         if not user_id:
#             return Response({"error": "user_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

#         queryset = self.filter_queryset(self.get_queryset())

#         if self.request.GET.get('page'):
#             paginated_data = self.paginate_queryset(queryset)

#             serializer = CreateItemListSerializer(paginated_data, many=True)

#             page_size = self.paginator.page.paginator.count // 20
#             if self.paginator.page.paginator.count % 20 == 0:
#                 page_size = page_size - 1
#             else:
#                 page_size = page_size + 1

#             response_data = {
#                 "links": {
#                     "next": self.paginator.get_next_link(),
#                     "previous": self.paginator.get_previous_link()
#                 },
#                 "page_size": page_size,
#                 "count": self.paginator.page.paginator.count,
#                 "data": serializer.data,
#             }
#             return Response(response_data, status=status.HTTP_200_OK)

#         serializer = CreateItemListSerializer(queryset, many=True)
#         return Response(serializer.data)
    


class ItemlistView(generics.ListAPIView):
    """
    A viewset that provides the list of items for a specific company
    """
    serializer_class = CreateItemListSerializer
    # permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [StartsWithSearchFilter]
    search_fields = ['tansaction__customer_name']

    def get_company_id(self):
        # Assuming you're passing company_id as a query parameter in the request
        return self.request.query_params.get('company_id', None)

    def get_queryset(self):
        company_id = self.get_company_id()

        if not company_id:
            return Item.objects.none()

        queryset = Item.objects.filter(tansaction__user__company__id=company_id).annotate(
            redflag=F('tansaction__red_flag')
        )

        return queryset.order_by('-redflag', 'tansaction')

    def list(self, request):
        company_id = self.get_company_id()

        if not company_id:
            return Response({"error": "company_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.filter_queryset(self.get_queryset())

        if self.request.GET.get('page'):
            paginated_data = self.paginate_queryset(queryset)

            serializer = CreateItemListSerializer(paginated_data, many=True)

            page_size = self.paginator.page.paginator.count // 20
            if self.paginator.page.paginator.count % 20 == 0:
                page_size = page_size - 1
            else:
                page_size = page_size + 1

            response_data = {
                "links": {
                    "next": self.paginator.get_next_link(),
                    "previous": self.paginator.get_previous_link()
                },
                "page_size": page_size,
                "count": self.paginator.page.paginator.count,
                "data": serializer.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        serializer = CreateItemListSerializer(queryset, many=True)
        return Response(serializer.data)






class MultiTransactionSecreenCalc(APIView):
    """
    A viewset that calculate the revenue and other things on multi transaction items 
    """
    serializer_class = TransactionScreenSerilizer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        ids = self.kwargs.get('ids')
        id_list = ids.split(',')
        tsc = Transaction.objects.filter(id__in=id_list)
        if len(tsc) > 0:
            return tsc
        else:
            None

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset == None:
            return Response({"message": "Transaction with this id does not exist"})
        calc_type = self.kwargs.get('typ')
        serializer = TransactionScreenSerilizer(
            queryset, many=True, context={'type': calc_type})
        data = serializer.data
        months = []
        table_total = total_calc2.table_totals(data)
        items_total = total_calc2.items_totals(data)

# -----------------------calculating months according to table---------------------------
        for i in range(0, len(table_total['temp_total_revenue'])):
            months.append(table_total['temp_total_revenue'][i]['date'])

        for i in range(0, len(table_total['total_billing_revenue'])):
            months.append(table_total['total_billing_revenue'][i]['date'])

        # for i in range (0, len(table_total['balance'])):
        #     months.append(table_total['balance'][i]['date'])

        for i in range(0, len(table_total['total_arr'])):
            months.append(table_total['total_arr'][i]['date'])

        # if len(months) > len(months_biling) and len(months) > len(months_deffred_revenue):
        #     ttl_months = months

        # if len(months_biling) > len(months_deffred_revenue) and len(months_biling) > len(months):
        #     ttl_months = months_biling
        # else:
        #     ttl_months = months_deffred_revenue
        # if len(ttl_months) < len(month_arr):
        #     ttl_months = month_arr
        months = list(set(months))
        months.sort(key=lambda x: parse_date(x))

        return Response({"data": serializer.data,
                         "total_revenue": table_total['temp_total_revenue'],
                         "total_billing": table_total['total_billing_revenue'],
                         "balance": table_total['balance'], "total_arr": table_total["total_arr"],
                         "total_cumilative_revenue": table_total['total_cumilative_revenue'],
                         "total_cumilative_billing": table_total['total_cumilative_billing'],
                         "total_items_rev": items_total['total_items_rev'],
                         "total_items_def": items_total['total_items_def'],
                         "total_items_bal": items_total['total_items_bal'],
                         "tables_headings": items_total['table_headings'],
                         "total_items_arr": items_total['total_items_arr'],
                        #  "tables_heading": items_total['table_heading'],
                         "months": months,
                         #  "months_biling": months_biling,
                         #  "months_deffred_revenue" : months_deffred_revenue
                         }
                        )












class ArrBySpecifcsCustomerView(APIView):
    """
    A viewset that calculates the arr of a customer based on customer_name in transactions.
    """
    serializer_class = ArrByCustomerIdSeriliazer

    def get_queryset(self, *args, **kwargs):
        ids = self.kwargs.get('ids')
        ids_list = ids.split(',') 
        company_id = self.kwargs.get('company_id')  # Assuming user_id is part of the URL
        return Transaction.objects.filter(
            id__in=ids_list, user__company__id=company_id
        ).order_by('customer_name').distinct('customer_name')

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        heading = []
        start = Item.objects.earliest('s_start_d').s_start_d
        end = Item.objects.exclude(s_end_d=None).order_by(
            '-s_end_d').first().s_end_d
        current_date = start

        while current_date <= end:
            heading.append(current_date.strftime("%b %y"))
            current_date += relativedelta(months=1)
        calc_type = self.kwargs.get('typ')
        company_id = self.kwargs.get('company_id')

        serializer = ArrByCustomerIdSeriliazer(queryset, many=True, context={
                                             "type": calc_type, "company_id": company_id})
        total_arr = total_calc2.total_arr_customer(serializer.data)
        data = serializer.data
        modified_data = []
        for item in serializer.data:
            item['total_arr'] = total_arr
            modified_data.append(item)

        return Response({"data": modified_data, "heading": heading})
    






class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if a company with the same name already exists
        name = serializer.validated_data.get('name')
        existing_company = Company.objects.filter(name=name).first()
        if existing_company:
            return Response({'error': 'Company with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Company deleted successfully'}, status=status.HTTP_200_OK)





class UserListByCompanyAPIView(generics.ListAPIView):
    serializer_class = RegisterGetSerializer
    # permission_classes = [IsAuthenticated]


    def get_queryset(self):
        company_id = self.kwargs['company_id']
        return CustomUser.objects.filter(company_id=company_id).exclude(role=4)

    # def get_queryset(self):
    #     company_id = self.kwargs['company_id']
    #     return CustomUser.objects.filter(company_id=company_id)











# class GetArrByCompanySpecifcsCustomerView(APIView):
#     """
#     A viewset that calculate the arr of customer on base on sutomer_name on transaction
#     """
#     serializer_class = ArrByidCustomerSeriliazer
#     # permission_classes = [IsAuthenticated]

#     def get_queryset(self, *args, **kwargs):
#         ids = self.kwargs.get('ids')
#         ids_list = ids.split(',')
#         company_id = self.kwargs.get('company_id')
#         return Transaction.objects.filter(
#             id__in=ids_list, user__company__id=company_id
#         ).order_by('customer_name').distinct('customer_name')

#     def get(self, request, *args, **kwargs):
#         # Note the use of `get_queryset()` instead of `self.queryset`
#         queryset = self.get_queryset()
#         heading = []
#         start = Item.objects.earliest('s_start_d').s_start_d
#         end = Item.objects.exclude(s_end_d=None).order_by(
#             '-s_end_d').first().s_end_d
#         current_date = start

#         while current_date <= end:
#             heading.append(current_date.strftime("%b %y"))
#             current_date += relativedelta(months=1)
#         calc_type = self.kwargs.get('typ')
#         company_id = self.kwargs.get('company_id')
#         print(".................................",)

#         serializer = ArrByidCustomerSeriliazer(queryset, many=True, context={
#                                              "type": calc_type, "user_id": company_id})
#         total_arr = total_calc2.total_arr_customer(serializer.data)
#         data = serializer.data
#         modified_data = []
#         for item in serializer.data:
#             item['total_arr'] = total_arr
#             modified_data.append(item)

#         return Response({"data": modified_data, "heading": heading})




class CustomerArrRollForwardView(APIView):

    serializer_class = ArrByCustomerIdSeriliazer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        ids = self.kwargs.get('ids')
        id_list = ids.split(',')
        return Transaction.objects.filter(id__in=id_list).order_by('customer_name').distinct('customer_name')

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        calc_type = self.kwargs.get('typ')
        company_id = self.kwargs.get('company_id')
        serializer = ArrByCustomerIdSeriliazer(queryset, many=True, context={
                                             'type': calc_type, "company_id": company_id})
        arr_roll_fwd = total_calc2.arr_rollforward(serializer.data)

        heading = []
        start = Item.objects.earliest('s_start_d').s_start_d
        end = Item.objects.exclude(s_end_d=None).order_by(
            '-s_end_d').first().s_end_d
        current_date = start

        while current_date <= end:
            heading.append(current_date.strftime("%b %y"))
            current_date += relativedelta(months=1)
        rsp = {"Beginning_ARR": arr_roll_fwd["Beginning_ARR"],
               "New_ARR": arr_roll_fwd["New_ARR"],
               "Recovery_ARR": arr_roll_fwd["Recovery_ARR"],
               "Expansion ARR": arr_roll_fwd["Expansion_ARR"],
               "Contraction_ARR": arr_roll_fwd["Contraction_ARR"],
               "Churn_ARR": arr_roll_fwd["Churn_ARR"],
            #    "Recovery_ARR": arr_roll_fwd["Recovery_ARR"],
               "Ending_ARR": arr_roll_fwd["Ending_ARR"],
               }
        side_heading = rsp.keys()

        return Response({"arr_roll_fwd": rsp, "heading": heading, "side_heading": side_heading,
                         "Logo_Rollforward": arr_roll_fwd['Logo_Rollforward']})
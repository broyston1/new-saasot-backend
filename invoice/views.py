from email import message
from functools import partial
import json
import os
import threading

from django.http import FileResponse, Http404
from django.db.models import F, Q


from django.db.models import Subquery
from django.core.cache import cache
from django.http import HttpResponse

from dateutil.relativedelta import relativedelta
from datetime import datetime

from rest_framework.response import Response
from rest_framework import status, viewsets, mixins, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import filters
from rest_framework.filters import OrderingFilter


from .serializers import (UploadCsvSerializer, CreateTransactionSerliazer, ItemSerializer, CreateItemListSerializer,
                          ItemRevenueSeriliazer, TransactionScreenSerilizer, ArrByCustomerSeriliazer, UpdateTransactionSerliazer,
                          CreateCalculationSeriliazer, CloseDateSeriliazer, ArrGracePeriodSerializer, CalculationDaySerializer,
                          PendingArrByCustomerSeriliazer
                          )
# from .reterive_invoice_data import load_membership_data
from .newret import load_membership_data
from .models import Transaction, Item, Calculation, CloseDate, ArrGracePeriod, CalculationMonths, Company
from .signals import calculation_on_arr_grace_period_handler
from services.models import ProductServiceType
# from .saasot_calculation.total_calc import table_totals, items_totals
from .saasot_calculation import total_calc2
from .saasot_calculation.revenue1 import *
from .csv_excel_download import create_arr_csv, create_arr_excel, create_database_contract_csv, create_database_contract_excel
from authentication.permissions import DuplicateInvoice, IsOwner, CalculationWrite, IsAdmin
from .pagination import CustomPagination
from .filters import StartsWithSearchFilter


# Create your views here.
# import logging

class UploadCsvView(APIView):
    """
    A viewset that provides the upload csv functionality 
    """
    serializer_class = UploadCsvSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        if 'csv_file' not in data.keys():
            return Response({"message": "'csv_file' key not found"}, status=status.HTTP_400_BAD_REQUEST)
        if data['csv_file']:
            serializer = UploadCsvSerializer(data=data)
            if serializer.is_valid():
                # print(self.request.GET.get('company_id'), "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPP")
                company_id = self.request.GET.get('company_id', None)
                # print(company_id, "LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLll")
                try:
                    company = Company.objects.get(id=company_id)
                    # print(company)
                except:
                    company = None

                print('============ company 1 ==============', company)
                undefiend_service = load_membership_data(data['csv_file'], request.user, company)

                # threading.Thread(target=load_membership_data, args=[data['csv_file'], request.user]).start()
                if undefiend_service.get('error', None):
                    return Response({'message': str(undefiend_service['error'])}, status=status.HTTP_400_BAD_REQUEST)
                return Response({"undefiend_service": undefiend_service, "message": "Succesfully upload!!"}, status=status.HTTP_200_OK)

            else:
                return Response({'message': 'There is an error in the data'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "file is required to send "}, status=status.HTTP_400_BAD_REQUEST)



class CreateTransactionView(viewsets.ModelViewSet):
    """
    A viewset that provides the all actions
    """
    serializer_class = CreateTransactionSerliazer
    queryset = Transaction.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [DuplicateInvoice, IsAuthenticated]
        elif self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsOwner, IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def create(self, request):
        # items = request.data['items']
        data = request.data.copy()
        items = json.loads(data['items'])
        # items = data['items']
        del data['items']

        transaction_serializer = CreateTransactionSerliazer(
            data=data, context={"request": request})
        if transaction_serializer.is_valid():
            transaction_serializer.save()
            transaction = transaction_serializer.data['id']

# -----------------------creating item here----------------------------
            for i in range(0, len(items)):
                items[i]['tansaction'] = transaction
            item_serializer = ItemSerializer(data=items, many=True)
            if item_serializer.is_valid():
                item_serializer.save()
                return Response({"message": "Succesfully Created"}, status=status.HTTP_201_CREATED)
            else:
                Transaction.objects.get(id=transaction).delete()
                return Response({'message': 'There is an error in items data', "error": item_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'There is an error in transaction data', "error": transaction_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        items = json.loads(data['items'])
        # items = data['items']
        del data['items']
        instance = self.get_object()
        item_instance = Item.objects.filter(
            tansaction__user__company=self.request.user.company, tansaction=instance)

        transaction_serializer = UpdateTransactionSerliazer(
            instance, data=data, partial=True)
        if transaction_serializer.is_valid():
            transaction_serializer.save()
            transaction = transaction_serializer.data['id']

            # -----------------------updating item here----------------------------
            for i in range(0, len(items)):
                items[i]['tansaction'] = transaction
            item_serializer = ItemSerializer(
                item_instance, data=items, many=True)
            if item_serializer.is_valid():
                Item.objects.filter(tansaction__id=transaction).delete()
                item_serializer.save()
                return Response({"message": "Sucesfully Updated"}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'There is an error in items data', "error": item_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'There is an error in transaction data', "error": transaction_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ItemlistView(generics.ListAPIView):
    """
    A viewset that provides the list of items of the specific user
    """
    serializer_class = CreateItemListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [StartsWithSearchFilter]
    search_fields = ['tansaction__customer_name']


    def get_queryset(self):
        # return Item.objects.filter(tansaction__user__company=self.request.user.company).order_by('tansaction')
        # Annotate the queryset with a Boolean field for 'tansaction__redflag' to order by
        items = Item.objects.filter(tansaction__user__company=self.request.user.company).annotate(
            redflag=F('tansaction__red_flag')
        )
        # Order the queryset first by 'redflag' in descending order, then by 'tansaction'
        return items.order_by('-redflag', 'tansaction')


    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.filter_queryset(self.get_queryset())

        if self.request.GET.get('page'):
            paginated_data = self.paginate_queryset(queryset)

            serializer = CreateItemListSerializer(paginated_data, many=True)

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
            }
            return Response(response_data, status=status.HTTP_200_OK)

        serializer = CreateItemListSerializer(queryset, many=True)
        return Response(serializer.data)


class DatabaseDropdownList(APIView):
    """
    An APi provide a deopdown list of database list table in frontend
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        new_list = []
        user = self.request.user
        prd_types = ProductServiceType.objects.filter(
            user__company=user.company)

        for prd in prd_types:
            new_list.append(
                {"name": str(prd.productp_service_type) + " revenue", "id": prd.id})
            new_list.append(
                {"name": str(prd.productp_service_type) + " deferred revenue", "id": prd.id})
        new_list.append({"name": "billing"})
        new_list.append({"name": "total revenue"})
        new_list.append({"name": "total deferred revenue"})
        return Response({"data": new_list}, status=status.HTTP_200_OK)


# ____________________start_code _by_davinder______________________________

class ArrByCustomerView(generics.ListAPIView):
    """
    A viewset that calculates the ARR of a customer based on the customer_name on transactions.
    """
    serializer_class = ArrByCustomerSeriliazer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [StartsWithSearchFilter, OrderingFilter]
    search_fields = ['customer_name']
    ordering_fields = ['customer_name']

    def get_queryset(self, *args, **kwargs):
        item_ids = Item.objects.filter(
            tansaction__user__company=self.request.user.company,
            productp_service__revenue_type__revenue_type="over life of subscription"
        ).values('tansaction_id')

        queryset = Transaction.objects.filter(
            id__in=item_ids, user__company=self.request.user.company
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

        if self.request.GET.get('page'):
            paginated_data = self.paginate_queryset(queryset)

            serializer = ArrByCustomerSeriliazer(
                paginated_data, many=True,
                context={"type": calc_type, "user": self.request.user}
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
    
  

  
    
# ____________________end_code _by_davinder______________________________

class ArrBySpecifcsCustomerView(APIView):
    """
    A viewset that calculate the arr of customer on base on sutomer_name on transaction
    """
    serializer_class = ArrByCustomerSeriliazer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        ids = self.kwargs.get('ids')
        ids_list = ids.split(',')
        return Transaction.objects.filter(
            id__in=ids_list, user__company=self.request.user.company
        ).order_by('customer_name').distinct('customer_name')

    def get(self, request, *args, **kwargs):
        # Note the use of `get_queryset()` instead of `self.queryset`
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

        serializer = ArrByCustomerSeriliazer(queryset, many=True, context={
                                             "type": calc_type, "user": self.request.user})
        total_arr = total_calc2.total_arr_customer(serializer.data)
        data = serializer.data
        modified_data = []
        for item in serializer.data:
            item['total_arr'] = total_arr
            modified_data.append(item)

        return Response({"data": modified_data, "heading": heading})


class MultiTransactionSecreenCalc(APIView):
    """
    A viewset that calculate the revenue and other things on multi transaction items 
    """
    serializer_class = TransactionScreenSerilizer
    permission_classes = [IsAuthenticated]

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


class CalculationViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the all actions
    """
    serializer_class = CreateCalculationSeriliazer
    queryset = Calculation.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAuthenticated, CalculationWrite]
            # permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def partial_update(self, request, *args, **kwargs):
        data = request.data.copy()
        rev_value = 0
        del data['password']
        instance = self.get_object()
        key = list(data.keys())
        data2 = {key[0]: json.loads(data[key[0]])}
        # data2 = {key[0]:data[key[0]]}
        f = 0

        # print(data, "::::::::::")
        # print(data2, "PPPPPPPPPPPPPPPPPP")
        if key[0] == 'revenue':
            for i in range(0, len(data2[key[0]])):
                rev_value += data2[key[0]][i]['value']
            f = rev_value - instance.items.total_revenue
            # if rev_value > instance.items.total_revenue:
            #     return Response(
            #         {"message": f"Your total revenue is exceeding the total value {f}"},
            #         status=status.HTTP_400_BAD_REQUEST
            #         )

            serializer = CreateCalculationSeriliazer(instance, data=data2)
            if serializer.is_valid():
                self.perform_update(serializer)
                serializer.save()
                calc_id = serializer.data['id']
                calc = Calculation.objects.get(id=calc_id)
                item = calc.items
                def_rev = deferred_revenue(item)
                calc.deffered_revenue = def_rev
                calc.save()
                return Response(serializer.data)
            else:
                return Response(
                    {"message": "there is something wrong with data",
                        "error": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

        else:
            serializer = CreateCalculationSeriliazer(instance, data=data2)
            if serializer.is_valid():
                self.perform_update(serializer)
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(
                    {"message": "there is something wrong with data",
                        "error": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )


class CloseDateViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CloseDateSeriliazer
    queryset = CloseDate.objects.all()


class ArrRollForwardView(APIView):

    serializer_class = ArrByCustomerSeriliazer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        item_ids = Item.objects.filter(
            Q(total_revenue__isnull=False) | Q(total_revenue__gt=0),
            tansaction__user__company=self.request.user.company,
            productp_service__revenue_type__revenue_type="over life of subscription"
        ).values('tansaction_id')

        # Retrieve unique transactions with transaction IDs from the above subquery
        return Transaction.objects.filter(
            id__in=Subquery(item_ids), user__company=self.request.user.company
        ).order_by('customer_name').distinct('customer_name')

    def get(self, request, *args, **kwargs):

        user = request.user
        cache_key = f"user_{user.id}_data"

        # Check if the response is cached for this user.
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset()
        calc_type = self.kwargs.get('typ')
        serializer = ArrByCustomerSeriliazer(queryset, many=True, context={
                                             'type': calc_type, "user": self.request.user})

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


class CustomerArrRollForwardView(APIView):

    serializer_class = ArrByCustomerSeriliazer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        ids = self.kwargs.get('ids')
        id_list = ids.split(',')
        return Transaction.objects.filter(id__in=id_list).order_by('customer_name').distinct('customer_name')

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        calc_type = self.kwargs.get('typ')
        serializer = ArrByCustomerSeriliazer(queryset, many=True, context={
                                             'type': calc_type, "user": self.request.user})
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

# s


class ArrGracePeriodViewset(viewsets.ModelViewSet):
    """
    A viewset that provides the detail and list  actions
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = ArrGracePeriodSerializer
    # queryset = ProductServiceType.objects.all(iser = self.request.user)

    def get_queryset(self):
        return ArrGracePeriod.objects.all()

    def create(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            ArrGracePeriod.objects.filter(
                company=request.user.company).delete()
            instance = serializer.save()
            calculation_on_arr_grace_period_handler(
                sender=self.__class__, instance=instance, created=True, user=request.user)

            return Response(
                {"message": "Succesfully updated", "data": serializer.data},
                status=status.HTTP_200_OK
            )
    # def create(self, request, *args, **kwargs):
    #     data = request.data
    #     serializer = self.serializer_class(data=data)

    #     if serializer.is_valid():
    #         # Get the user's company and create or update the ArrGracePeriod instance
    #         company = request.user.company
    #         instance, created = ArrGracePeriod.objects.get_or_create(company=company, defaults=serializer.validated_data)

    #         if not created:
    #             instance.months = serializer.validated_data.get('months', instance.months)
    #             instance.save()

    #         calculation_on_arr_grace_period_handler(sender=self.__class__, instance=instance, created=True, user=request.user)
    #         return Response(
    #             {"message": "Successfully updated", "data": serializer.data},
    #             status=status.HTTP_200_OK
    #         )

    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response("this method is not allowed")

    def destroy(self, request, *args, **kwargs):
        return Response("this method is not allowed")


class StartEndPeriod(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        starting_period = []
        start_p = parse_date("Jan 16")
        start_p_end = parse_date("Nov 29")
        current_date = start_p
        while current_date <= start_p_end:
            starting_period.append(current_date.strftime("%b %y"))
            current_date += relativedelta(months=1)

        ending_period = []
        start_p = parse_date("Jan 16")
        start_p_end = parse_date("Nov 29")
        current_date = start_p
        while current_date <= start_p_end:
            ending_period.append(current_date.strftime("%b %y"))
            current_date += relativedelta(months=1)

        return Response({"starting_period": starting_period, "ending_period": ending_period}, status=status.HTTP_200_OK)

# ___________________________________________________start_today___________________________






class ItemRevenueView(generics.ListAPIView):
    """
    A viewset that calculate the revenue and itemother things on  based
    """
    serializer_class = CalculationDaySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [StartsWithSearchFilter]
    search_fields = ['items__tansaction__customer_name']

    def get_ordering(self):
        ordering = self.request.query_params.get('ordering')
        return ordering

    def get_queryset(self, *args, **kwargs):
        queryset = Calculation.objects.filter(
            items__tansaction__user__company=self.request.user.company)
        if self.kwargs.get('typ') != 'day':
            queryset = CalculationMonths.objects.filter(
                items__tansaction__user__company=self.request.user.company)

        # queryset = queryset.order_by('items__transaction')
        queryset = self.filter_queryset(queryset)

        query = self.kwargs.get('query')
        query_list = query.split(' ')

        if "billing" in query or 'total' in query:
            pass
        else:
            queryset = queryset.filter(items__tansaction__user__company=self.request.user.company,
                                       items__productp_service__productp_service_type__productp_service_type=query_list[
                                           0]
                                       ).order_by('items__s_start_d')

        # Apply additional ordering based on the 'ordering' parameter
        ordering = self.get_ordering()
        if ordering:
            queryset = queryset.order_by(ordering)

        # Modify the queryset based on query parameters
        return_fields = ['revenue', 'billing', 'deffered_revenue']
        if "deferred" in query:
            return_fields.remove('deffered_revenue')
        elif "billing" in query:
            return_fields.remove('billing')
        else:
            return_fields.remove('revenue')

        self.return_fields = return_fields
        # Transaction.objects.filter(user__company=self.request.user.company).delete()
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

        return Response({"data": serializer.data, "heading": heading}, status=status.HTTP_200_OK)








# ___________________________________________________end_today___________________________

# class ItemRevenueView(generics.ListAPIView):
#     """
#     A viewset that calculate the revenue and itemother things on  based
#     """
#     serializer_class = CalculationDaySerializer
#     permission_classes = [IsAuthenticated]
#     pagination_class = CustomPagination
#     filter_backends = [StartsWithSearchFilter]
#     search_fields = ['items__tansaction__customer_name']

#     def get_ordering(self):
#         ordering = self.request.query_params.get('ordering')
#         return ordering

#     def get_queryset(self, *args, **kwargs):
#         queryset = Calculation.objects.filter(
#             items__tansaction__user__company=self.request.user.company)
#         if self.kwargs.get('typ') != 'day':
#             queryset = CalculationMonths.objects.filter(
#                 items__tansaction__user__company=self.request.user.company)

#         # queryset = queryset.order_by('items__transaction')
#         queryset = self.filter_queryset(queryset)

#         query = self.kwargs.get('query')
#         query_list = query.split(' ')

#         if "billing" in query or 'total' in query:
#             pass
#         else:
#             queryset = queryset.filter(items__tansaction__user__company=self.request.user.company,
#                                        items__productp_service__productp_service_type__productp_service_type=query_list[
#                                            0]
#                                        ).order_by('items__s_start_d')

#         # Apply additional ordering based on the 'ordering' parameter
#         ordering = self.get_ordering()
#         if ordering:
#             queryset = queryset.order_by(ordering)

#         # Modify the queryset based on query parameters
#         return_fields = ['revenue', 'billing', 'deffered_revenue']
#         if "deferred" in query:
#             return_fields.remove('deffered_revenue')
#         elif "billing" in query:
#             return_fields.remove('billing')
#         else:
#             return_fields.remove('revenue')

#         self.return_fields = return_fields
#         # Transaction.objects.filter(user__company=self.request.user.company).delete()
#         return queryset

#     def list(self, request, *args, **kwargs):
#         start = parse_date(self.kwargs.get('start'))
#         end = parse_date(self.kwargs.get('end'))
#         current_date = start
#         heading = []

#         while current_date <= end:
#             heading.append(current_date.strftime("%b %y"))
#             current_date += relativedelta(months=1)

#         queryset = self.filter_queryset(self.get_queryset())

#         if self.request.GET.get('page'):
#             paginated_data = self.paginate_queryset(queryset)

#             serializer = CalculationDaySerializer(
#                 paginated_data, many=True, fields=self.return_fields)

#             page_size = self.paginator.page.paginator.count // 20
#             if self.paginator.page.paginator.count % 20 == 0:
#                 page_size = page_size-1
#             else:
#                 page_size = page_size+1

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
#             serializer = CalculationDaySerializer(
#                 queryset, many=True, fields=self.return_fields)

#         return Response({"data": serializer.data, "heading": heading}, status=status.HTTP_200_OK)











class TableTotal(APIView):

    def get_queryset(self, *args, **kwargs):
        queryset = Calculation.objects.filter(
            items__tansaction__user__company=self.request.user.company)
        if self.kwargs.get('typ') != 'day':
            queryset = CalculationMonths.objects.filter(
                items__tansaction__user__company=self.request.user.company)

        query = self.kwargs.get('query')
        query_list = query.split(' ')

        if "billing" in query or 'total' in query or 'arr' in query:
            pass

        else:
            queryset = queryset.filter(items__tansaction__user__company=self.request.user.company,
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


class DownloadArrCustomer(APIView):
    """
    A viewset that provide the csv of arr-by-customer
    """

    def get_queryset(self, *args, **kwargs):

        start = parse_date(self.kwargs.get('start'))
        end = parse_date(self.kwargs.get('end'))

        item_ids = Item.objects.filter(
            tansaction__user__company=self.request.user.company,
            productp_service__revenue_type__revenue_type="over life of subscription",
            s_start_d__date__gte=start, s_end_d__date__lte=end
        ).values('tansaction_id')

        return Transaction.objects.filter(id__in=item_ids, user__company=self.request.user.company).order_by('customer_name').distinct('customer_name')

    def get(self, request, *args, **kwargs):

        queryset = self.get_queryset()
        calc_type = self.kwargs.get('typ')

        seriliazer = ArrByCustomerSeriliazer(queryset, many=True, context={
                                             "type": calc_type, "user": self.request.user})
        file_type = self.kwargs.get('file')

        if file_type == 'csv':
            threading.Thread(target=create_arr_csv, args=[
                             seriliazer.data, self.request.user.username]).start()
            return Response({'message': 'Task started in the background', 'file_name': f'{self.request.user.username}-arr.csv'},
                            status=status.HTTP_200_OK
                            )
        else:
            threading.Thread(target=create_arr_excel, args=[
                             seriliazer.data, self.request.user.username]).start()
            return Response({'message': 'Task started in the background', 'file_name': f'{self.request.user.username}-arr.xlsx'},
                            status=status.HTTP_200_OK
                            )


class DownloadDatabaseContract(APIView):

    """
    A viewset that provide the csv of database-contract-table
    """
    serializer_class = CalculationDaySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self, *args, **kwargs):
        queryset = Calculation.objects.filter(
            items__tansaction__user__company=self.request.user.company)
        if self.kwargs.get('typ') != 'day':
            queryset = CalculationMonths.objects.filter(
                items__tansaction__user__company=self.request.user.company)

        query = self.kwargs.get('query')
        query_list = query.split(' ')

        if "billing" in query or 'total' in query:
            pass

        else:
            if self.kwargs.get('file') == 'csv':
                queryset = queryset.filter(items__tansaction__user__company=self.request.user.company,
                                           items__productp_service__productp_service_type__productp_service_type=query_list[0]
                                           ).order_by('items__s_start_d')
            else:
                queryset = queryset.filter(items__tansaction__user__company=self.request.user.company
                                           ).order_by('items__s_start_d')

        # Modify the queryset based on query parameters
        return_fields = ['revenue', 'billing', 'deffered_revenue']
        fld = ""
        if "deffered" in query:
            return_fields.remove('deffered_revenue')
            fld = "deffered_revenue"
        elif "billing" in query:
            return_fields.remove('billing')
            fld = "billing"
        else:
            fld = "revenue"
            return_fields.remove('revenue')

        # self.return_fields = return_fields
        file_type = self.kwargs.get('file')
        if file_type != 'csv':
            self.return_fields = []
        else:
            self.return_fields = return_fields
        self.fld = fld
        return queryset.order_by('items__s_start_d')

    def get(self, request, *args, **kwargs):

        start = parse_date(self.kwargs.get('start'))
        end = parse_date(self.kwargs.get('end'))
        task_id = self.request.user.username

        queryset = self.get_queryset().filter(
            Q(items__s_start_d__date__isnull=True) | Q(items__s_end_d__date__isnull=True) |
            (Q(items__s_start_d__date__gte=start)
             & Q(items__s_end_d__date__lte=end))
        )

        # if len(queryset) > 5000:
        #     return Response({"message": "Please decrease the range between Start_date and End_date"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CalculationDaySerializer(
            queryset, many=True, fields=self.return_fields)

        file_type = self.kwargs.get('file')

        if file_type == 'csv':
            threading.Thread(target=create_database_contract_csv, args=[
                             serializer.data, self.fld, self.request.user.username]).start()
            return Response({'message': 'Task started in the background', 'file_name': f'{self.request.user.username}.csv'},
                            status=status.HTTP_200_OK
                            )

        else:
            threading.Thread(target=create_database_contract_excel, args=[
                             serializer.data, self.request.user.username]).start()
            # print("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            return Response({'message': 'Task started in the background', 'file_name': f'{self.request.user.username}.xlsx'},
                            status=status.HTTP_200_OK
                            )


class DownloadFile(APIView):

    def get(self, request, *args, **kwargs):

        file_name = self.kwargs.get('name')
        if os.path.exists(file_name):
            response = FileResponse(open(
                file_name, 'rb'), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="output.xlsx"'
            os.remove(file_name)
            return response
        else:
            return Response({"message": "Processing"}, status=status.HTTP_404_NOT_FOUND)


class ClearUserCacheView(APIView):

    def get(self, request, *args, **kwargs):
        # Construct a unique cache key for the user based on user_id
        user = request.user
        cache_key = f"user_{user.id}_data"
        cache_key2 = f"user_{user.id}_pending_arr"

        # Delete the cache for the specific user
        cache.delete(cache_key)
        cache.delete(cache_key2)

        return Response({'message': f'Cache cleared for user {user.id}'})


class PendingArr(APIView):

    serializer_class = ArrByCustomerSeriliazer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        item_ids = Item.objects.filter(
            Q(total_revenue__isnull=False) | Q(total_revenue__gt=0),
            tansaction__user__company=self.request.user.company,
            productp_service__revenue_type__revenue_type="over life of subscription"
        ).values('tansaction_id')

        # Retrieve unique transactions with transaction IDs from the above subquery
        return Transaction.objects.filter(
            id__in=Subquery(item_ids), user__company=self.request.user.company
        ).order_by('customer_name').distinct('customer_name')

    def get(self, request, *args, **kwargs):

        user = request.user
        cache_key = f"user_{user.id}_pending_arr"

        # Check if the response is cached for this user.
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset()
        calc_type = self.kwargs.get('typ')
        serializer = PendingArrByCustomerSeriliazer(
            queryset, many=True, context={'type': calc_type, "user": self.request.user})

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

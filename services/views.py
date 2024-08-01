import re
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from .serializers import (ProductServiceSerializer, ProductServiceTypeSerializer, RevenueTypeSerializer,
                           UndefiendProductServiceSerializer, CreateProductServiceSerializer, ExpectedMonthsSerializer
                           )
from .models import ProductService, ProductServiceType, RevenueType, ExpectedMonths
from invoice.models import Item
from invoice.serializers import CreateItemListSerializer
from authentication.permissions import DuplicatePriductService, IsOwner
from authentication.models import CustomUser, Company
from .convertor import Create_csv, Create_xslx
from .signals import calculation_on_expected_life_save


# Create your views here.
class ProductServiceViewset(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    serializer_class = CreateProductServiceSerializer
    queryset = ProductService.objects.all()
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [DuplicatePriductService, IsAuthenticated]
        elif self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsOwner, IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return ProductServiceSerializer
        return self.serializer_class

    def get_queryset(self):
        # ProductService.objects.filter(user__company=self.request.user.company).delete
        return ProductService.objects.filter(company=self.request.user.company).order_by('-is_active')

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        print('data data data === ',data);

# --------------------if product-service already in database but not active--------------------------
        if 'service_id' in request.data:
            print("--------------------------------")
            data = request.data.copy()
            try:
                instance = ProductService.objects.get(id=data['service_id'])
            except ProductService.DoesNotExist:
                return Response({"message": "product-service  with this id does not found"}, status=status.HTTP_404_NOT_FOUND)
            try:
                productp_service_type = ProductServiceType.objects.get(id=data['productp_service_type'])
            except ProductService.DoesNotExist:
                return Response({"message": "product-service-type  with this id does not found"}, status=status.HTTP_404_NOT_FOUND)
            try:
                revenue_type = RevenueType.objects.get(id=data['revenue_type'])
            except ProductService.DoesNotExist:
                return Response({"message": "revenue-type  with this id does not found"}, status=status.HTTP_404_NOT_FOUND)

            instance.productp_service_type = productp_service_type
            instance.revenue_type = revenue_type
            instance.is_active = True
            instance.save()
            return Response({"message": "sucesfully upload"}, status=status.HTTP_201_CREATED)

        print(data, "-------------------------------")
        data['company'] = request.user.company_id
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "sucesfully upload"}, status=status.HTTP_200_OK)
        else:
            default_errors = serializer.errors
            field_names = []
            for field_name, field_errors in default_errors.items():
                field_names.append(field_name)

            return Response({'error': f'Invalid data in {field_names}'}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        items=Item.objects.filter(productp_service=instance, s_start_d__isnull=True)
        revenue_type = RevenueType.objects.get(id = request.data['revenue_type'])
        if revenue_type.revenue_type == "over life of subscription" and len(items)>0:
            item_serializer = CreateItemListSerializer(items, many=True)
            return Response({"message":"please correct date in this items", "items":item_serializer.data })
            
        else:
            serializer = CreateProductServiceSerializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            serializer.save()
            return Response(serializer.data)

# Create your views here.
class ProductServiceTypeViewset(viewsets.ModelViewSet):
    """
    A viewset that provides the detail and list  actions
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProductServiceTypeSerializer

    def get_queryset(self):
        return ProductServiceType.objects.filter(user__company = self.request.user.company)


class RevenueTypeViewset(viewsets.ModelViewSet):
    """
    A viewset that provides the list and detail actions
    """
    permission_classes = [IsAuthenticated]
    serializer_class = RevenueTypeSerializer
    queryset = RevenueType.objects.all()


class DefiendProductServiceViewset(generics.ListCreateAPIView):
    """
    A viewset that provides the list and detail actions
    """
    # queryset = ProductService.objects.filter(is_active=True)
    serializer_class = UndefiendProductServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProductService.objects.filter(user__company=self.request.user.company, is_active=True)

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = UndefiendProductServiceSerializer(queryset, many=True)
        return Response(serializer.data)


class UndefiendProductServiceViewset(generics.ListCreateAPIView):
    """
    A viewset that provides the list and detail actions
    """
    # queryset = ProductService.objects.filter(is_active=True)
    serializer_class = UndefiendProductServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProductService.objects.filter(user__company=self.request.user.company, is_active=False)

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = UndefiendProductServiceSerializer(queryset, many=True)
        return Response(serializer.data)
    
#  ===+++++++++++++++++++++++++========================== prince code    started ---------------------------+++++++++++++++++++=========
class DownloadProductService(APIView):

    serializer_class = ProductServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProductService.objects.filter(user__company=self.request.user.company, is_active=True)

    def get(self, request, *args, **kwargs):

        queryset = self.get_queryset()

        seriliazer = ProductServiceSerializer(queryset, many=True)
        file_type = self.kwargs.get('file')

        if file_type =='csv':
            file = Create_csv(seriliazer.data)
            response = Response(file, content_type='text/csv', status=status.HTTP_200_OK)
            response['Content-Disposition'] = 'attachment; filename="output_file.csv"'

            return response

        else:
            file =  Create_xslx(seriliazer.data)
            response = HttpResponse(file.read(),
                        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="output_file.xlsx"'

            return response
        

class ExceptedMonthsViewset(viewsets.ModelViewSet):
   
    permission_classes = [IsAuthenticated]
    serializer_class = ExpectedMonthsSerializer
    queryset = ExpectedMonths.objects.all()
    
    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            # Get the user's company and create or update the ExpectedMonths instance
            company = request.user.company
            instance, created = ExpectedMonths.objects.get_or_create(company=company, defaults=serializer.validated_data)

            if not created:
                instance.months = serializer.validated_data.get('months', instance.months)
                instance.save()

            obj = RevenueType.objects.get(revenue_type = 'over the expected life of the customer')
            calculation_on_expected_life_save(sender=self.__class__, instance=obj, created=False, user=request.user)
            return Response(
                {"message": "Successfully updated", "data": serializer.data},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    





# ______________________________________data_get_by_id_by_davinder___________________________________________
    
class ProductGetByServiceIdTypeViewSet(viewsets.ModelViewSet):
    queryset = ProductServiceType.objects.all()
    serializer_class = ProductServiceTypeSerializer
    permission_classes = [AllowAny]  # AllowAny for simplicity, adjust as needed

    def get_queryset(self):
        company_id = self.kwargs.get('company_id')  # Assuming you pass 'company_id' in the URL
        print(company_id, "OOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        return ProductServiceType.objects.filter(company__id=company_id)



    # def get_queryset(self):
    #     user_id = self.kwargs.get('user_id')  # Assuming you pass 'user_id' in the URL
    #     return ProductServiceType.objects.filter(user_id=user_id)
    

    def create(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')

        # Create a mutable copy of the QueryDict
        mutable_data = request.data.copy()

        # Modify the mutable copy
        mutable_data['user'] = user_id

        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')

        print('user_id user_id == ', user_id)
        instance = get_object_or_404(ProductServiceType, user_id=user_id, pk=kwargs['pk'])
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()





# class GetProductByIdServiceViewset(viewsets.ModelViewSet):
#     serializer_class = ProductServiceSerializer
#     queryset = ProductService.objects.all()

#     def get_queryset(self):
#         user_id = self.kwargs.get('user_id', None)
#         company_id = self.kwargs.get('company_id', None)

#         if user_id is None:
#             return ProductService.objects.none()

#         queryset = ProductService.objects.filter(user=user_id)

#         if company_id:
#             # If company_id is provided, filter by both user_id and company_id
#             queryset = queryset.filter(user__company__id=company_id)

#         # Order the queryset based on 'is_active'
#         return queryset.order_by('is_active')








# class GetProductByIdServiceViewset(generics.ListCreateAPIView):
#     """
#     A viewset that provides the list and detail actions
#     """
#     # serializer_class = UndefiendProductServiceSerializer
#     serializer_class = ProductServiceSerializer

#     def get_queryset(self):
#         company_id = self.request.query_params.get('company_id')
#         if company_id is not None:
#             return ProductService.objects.filter(user__company__id=company_id)
#         else:
#             return ProductService.objects.none()  # or any other default queryset

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         serializer = ProductServiceSerializer(queryset, many=True)
#         return Response(serializer.data)



class GetProductByIdServiceViewset(viewsets.ModelViewSet):
    """
    A viewset that provides the list and detail actions
    """
    serializer_class = ProductServiceSerializer
    queryset = ProductService.objects.all()

    def get_queryset(self):
        company_id = self.request.query_params.get('company_id')
        print(self.kwargs, "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPP")
        print(company_id, ":::::::::::::::::::::::")
        if company_id is not None:
            return ProductService.objects.filter(company__id=company_id)
        else:
            print("OOOOOOOOOOOOOOOOOOOOOOOOO")
            return ProductService.objects.none()  


    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        print(data,"((((((((((((((((((((((()))))))))))))))))))))))")
# --------------------if product-service already in database but not active--------------------------
        if 'service_id' in request.data:
            print("--------------------------------")
            data = request.data.copy()
            try:
                instance = ProductService.objects.get(id=data['service_id'])
            except ProductService.DoesNotExist:
                return Response({"message": "product-service  with this id does not found"}, status=status.HTTP_404_NOT_FOUND)
            try:
                productp_service_type = ProductServiceType.objects.get(id=data['productp_service_type'])
            except ProductService.DoesNotExist:
                return Response({"message": "product-service-type  with this id does not found"}, status=status.HTTP_404_NOT_FOUND)
            try:
                revenue_type = RevenueType.objects.get(id=data['revenue_type'])
            except ProductService.DoesNotExist:
                return Response({"message": "revenue-type  with this id does not found"}, status=status.HTTP_404_NOT_FOUND)

            instance.productp_service_type = productp_service_type
            instance.revenue_type = revenue_type
            instance.is_active = True
            instance.save()

            return Response({"message": "sucesfully upload"}, status=status.HTTP_201_CREATED)

        else:
            company_id = self.request.query_params.get('company_id')
            user = CustomUser.objects.get(company__id=company_id)
            data['user'] = user.id
            print(data, ":::::::::::::::::::::::::::;;;;")
            serializer = CreateProductServiceSerializer(data=data)

            if serializer.is_valid():
                serializer.save()

                return Response(
                {"message": "Successfully created", "data": serializer.data},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        productp_service_type_id = self.request.data.get('productp_service_type')
        revenue_type_id = self.request.data.get('revenue_type')

        if productp_service_type_id:
            productp_service_type = ProductServiceType.objects.get(id=productp_service_type_id)
            serializer.validated_data['productp_service_type'] = productp_service_type

        if revenue_type_id:
            revenue_type = RevenueType.objects.get(id=revenue_type_id)
            serializer.validated_data['revenue_type'] = revenue_type

        serializer.save()



# ______________________________________data_get_by_id_by_davinder___________________________________________




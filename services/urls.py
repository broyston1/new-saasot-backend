from django.urls import path
from rest_framework import routers
from .views import UndefiendProductServiceViewset, DefiendProductServiceViewset, DownloadProductService,ProductGetByServiceIdTypeViewSet,GetProductByIdServiceViewset
from . import views

router = routers.DefaultRouter()
router.register(r'product-service', views.ProductServiceViewset, basename='product-service'),
router.register(r'product-type', views.ProductServiceTypeViewset, basename='product-service-type'),
router.register(r'revenue-type', views.RevenueTypeViewset, basename='revenue-type'),
router.register(r'expected-months', views.ExceptedMonthsViewset, basename='exoected-months'),
router.register(r'product_service', GetProductByIdServiceViewset, basename='product')
# _________________________startget_data_by_id_add_by_davinder)_________________________________________





# _________________________endget_data_by_id_add_by_davinder+++++++++++++++++++++++++++++++++++++++++++++++++

urlpatterns = [
    path('undefined-service', UndefiendProductServiceViewset.as_view(), name='undefined-service'),
    path('defined-service', DefiendProductServiceViewset.as_view(), name='defined-service'),
    path('download-Product-service/<str:file>/', DownloadProductService.as_view(), name='database-total'),

    # ________________________________________ad)by_davinder_____________________

    path('product-service-types/<int:company_id>/', ProductGetByServiceIdTypeViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-service-types-list'),
    path('product-service-types/<int:user_id>/<int:pk>/', ProductGetByServiceIdTypeViewSet.as_view({'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='product-service-types-detail'),
    # path('product_service/<int:user_id>/<int:company_id>/', GetProductByIdServiceViewset.as_view({'get': 'list'}), name='product-service-list'),
    # path('product_service/', GetProductByIdServiceViewset.as_view(), name='product_service'),
    # path('product_service/', GetProductByIdServiceViewset.as_view(), name='product_service'),
    # path('product_service/<int:pk>/', GetProductByIdServiceViewset.as_view(), name='specific_product_service'),
   
]

urlpatterns += router.urls

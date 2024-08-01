from django.urls import path
from rest_framework import routers
from .views import* 
from . import views

router = routers.DefaultRouter()
# router.register(r'revenue', views.ItemRevenueView, basename='revenue'),
# router.register(r'transaction', views.CreateTransactionView, basename='create-invoice'),


urlpatterns = [
    path('quickbook_oauth', QuickbookOauth.as_view(), name='quickbook_oauth'),
    path('quickbook-oauth-callback', QuickbookCallback.as_view(), name='quickbook_oauth_callback'),
    path('sync-invoice', SyncInvoice.as_view(), name='sync-invoice'),
    path('sync-product', SyncProduct.as_view(), name='sync-product'),
] 
urlpatterns += router.urls
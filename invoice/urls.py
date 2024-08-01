from django.urls import path
from rest_framework import routers
from .views import* 
from . import views
from django.views.decorators.cache import cache_page

router = routers.DefaultRouter()
# router.register(r'revenue', views.ItemRevenueView, basename='revenue'),
router.register(r'transaction', views.CreateTransactionView, basename='create-invoice'),
router.register(r'calculation', views.CalculationViewSet, basename='calculation'),
router.register(r'close-date', views.CloseDateViewSet, basename='closedate')
router.register(r'arr-grace-period', views.ArrGracePeriodViewset, basename='arr-grace-period')

urlpatterns = [
    path('upload-csv/', UploadCsvView.as_view(), name='upload-csv'),
    # path('create', CreateTransactionView.as_view(), name='create-invoice'),
    path('list', ItemlistView.as_view(), name='invoice-list'),
    path('revenue/<str:query>/<str:start>/<str:end>/<str:typ>/', ItemRevenueView.as_view(), name='revenue' ),
    # path('transaction-secreen/<int:pk>', TransactionSecreenCalc.as_view(), name='transaction-secreen'),
    path('multi-transaction-secreen/<str:ids>/<str:typ>', MultiTransactionSecreenCalc.as_view(), name='transaction-secreen'),
    path('arr-customer/<str:start>/<str:end>/<str:typ>/', ArrByCustomerView.as_view(), name='arr-by-customer' ),
    path('arr-customer/<str:ids>/<str:typ>', ArrBySpecifcsCustomerView.as_view(), name='arr-by-customer-specific'),
    path('arr-rollforward/<str:start>/<str:end>/<str:typ>', ArrRollForwardView.as_view(), name='arr-roll-forward' ),
    # path('arr-rollforward/<str:start>/<str:end>/<str:typ>',
    #      cache_page(60 * 15)(ArrRollForwardView.as_view()),  # Cache for 15 minutes (adjust as needed)
    #      name='arr-roll-forward'),
    path('arr-rollforward/<str:ids>/<str:typ>', CustomerArrRollForwardView.as_view(), name='customer-arr-roll-forward' ),
    path('pending_arr/<str:start>/<str:end>/<str:typ>', PendingArr.as_view(), name='peninding-arr' ),
    path('start-end/', StartEndPeriod.as_view(), name='start-end'),
    path('database-dropdown-list/', DatabaseDropdownList.as_view(), name='database-dropdown-list'),
    path('table-total/<str:query>/<str:typ>/', TableTotal.as_view(), name='database-total'),
    path('download-csv-arr/<str:file>/<str:typ>/<str:start>/<str:end>/', DownloadArrCustomer.as_view(), name='database-total'),
    path('download-csv-database-table/<str:file>/<str:query>/<str:typ>/<str:start>/<str:end>/', DownloadDatabaseContract.as_view(), name='database-total'),
    path('clear-user-cache/', ClearUserCacheView.as_view(), name='clear-user-cache'),
    path('download-file/<str:name>/', DownloadFile.as_view(), name='download_file'),


]
urlpatterns += router.urls
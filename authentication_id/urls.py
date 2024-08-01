from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')

urlpatterns = [
    path('users_by_id/', UserListView.as_view(), name='user-list'),
    # path('database-dropdown-list/', DatabaseDropdownList.as_view(), name='database-dropdown-list'),
  
    
    # path('start-end/<int:user_id>/', StartEndPeriod.as_view(), name='start_end_period'),
    # path('table-total/<int:user_id>/<str:query>/<str:typ>/', TableTotal.as_view(), name='database-total'),
    # path('arr-rollforward/<str:start>/<str:end>/<str:typ>/<int:user_id>/<int:company_id>', ArrRollForwardView.as_view(), name='arr-roll-forward'),
    path('upload-csv', UploadCsvView.as_view(), name='upload-csv'),
    path('multi-transaction-secreen/<str:ids>/<str:typ>', MultiTransactionSecreenCalc.as_view(), name='transaction-secreen'),
    # path('arr-customer/<str:ids>/<str:typ>/<int:user_id>/', ArrBySpecifcsCustomerView.as_view(), name='arr-by-customer-specific'),
   
    # path('revenue/<int:user_id>/<int:company_id>/<str:query>/<str:start>/<str:end>/<str:typ>/', ItemRevenueView.as_view(), name='revenue'),
    
    # ________________________api to get data based on company_id_______________________________________

    path('database-dropdown-list/<int:user_id>/', DatabaseDropdownList.as_view(), name='database-dropdown-list'),
    path('users/by-company/<int:company_id>/', UserListByCompanyAPIView.as_view(), name='user-list-by-company'),
    path('revenue/<int:company_id>/<str:query>/<str:start>/<str:end>/<str:typ>/', ItemRevenueView.as_view(), name='revenue'),
    # path('company-names/', CompanyNamesAPIView.as_view(), name='company-names-api'),
    path('arr-rollforward/<str:start>/<str:end>/<str:typ>/<int:company_id>/', ArrRollForwardView.as_view(), name='arr-roll-forward'),
    path('table-total/<int:company_id>/<str:query>/<str:typ>/', TableTotal.as_view(), name='database-total'),
    path('items/', ItemlistView.as_view(), name='item-list'),
    path('arr-customer/<int:company_id>/<str:start>/<str:end>/<str:typ>/', ArrByCustomerView.as_view(), name='arr-by-customer'),
    path('pending_arr/<int:company_id>/<str:start>/<str:end>/<str:typ>', PendingArr.as_view(), name='peninding-arr' ),
    path('clear-user-cache/<int:company_id>/', ClearUserCacheView.as_view(), name='clear-user-cache'),
    path('arr-rollforward/<str:ids>/<str:typ>/<int:company_id>/', CustomerArrRollForwardView.as_view(), name='customer-arr-roll-forward' ),
    path('arr-customer/<str:ids>/<str:typ>/<int:company_id>/', ArrBySpecifcsCustomerView.as_view(), name='arr-by-customer-specific'),
 

]   
urlpatterns += router.urls

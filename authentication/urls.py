from django.urls import path
from .views import VerifyEmail, LoginView, ForgetPassword,ResetPassword, RegistrationCompanyUserView,UserByRoleAPIView,UserListView
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'user', views.RegistrationView, basename='registerviews'),
# router.register(r'file-read', views.Fileviewset, basename='file_read'),
router.register(r'user_update', views.UserUpdateViewSet)




urlpatterns = [
    # path('register/', RegistrationView.as_view(), name='registerview'),
    path('verify-email/<str:uid>/<str:token>/', VerifyEmail.as_view(), name='verify_email'),
    path('login/', LoginView.as_view(), name='loginview'),
    path('forget-password/', ForgetPassword.as_view(), name='forget-password'),
    path('reset-password/<str:token>/<str:uid>/', ResetPassword.as_view(), name='reset-password'),
    path('signup-company-user/', RegistrationCompanyUserView.as_view(), name='signup-company-user'),
    # _______________________code_by_davinder_rajput)))))))))))))))))))))))))))))))))))))))))))))))))))

    # path('user-by-role/<int:role>/', UserByRoleAPIView.as_view(), name='user-by-role')
    path('usersaaaa/<int:id>/', UserByRoleAPIView.as_view(), name='user-detail'),
    path('users/', UserListView.as_view(), name='user-list'),

    
]
urlpatterns += router.urls

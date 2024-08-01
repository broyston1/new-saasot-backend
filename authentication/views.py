import uuid
from django.core.cache import cache
from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from .serializers import (RegisterSerializer, UserSerializer, SendForgotEmailSerializer, ChangePasswordSerializer,CustomUserSerializer,
                            RegisterUpdateSerializer, CompanySerializer, RegisterGetSerializer,UserUpdateSerializer,UserRegisterSerializer)
from .models import CustomUser, Company
from rest_framework.response import Response
from rest_framework import status
from rest_framework import status, viewsets
# from rest_framework_simplejwt.tokens import RefreshToken
from .helper import StringEncoder
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from saasot.settings import EMAIL_HOST_USER,FRONTEND_SITE_URL
from django.core.mail import send_mail
import uuid
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from datetime import timedelta
import datetime
from datetime import date, datetime, timedelta
import os
from django.shortcuts import get_object_or_404
from .permissions import IsAdmin



# Create your views here.


class RegistrationView(viewsets.ModelViewSet):
    serializer_class = RegisterSerializer
    permission_classes = [IsAdmin, IsAuthenticated]
    queryset = CustomUser.objects.all()

    def get_queryset(self):
        if self.request.user.role == 4:
             return CustomUser.objects.all()
        return CustomUser.objects.filter(company=self.request.user.company)
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAdmin, IsAuthenticated]
        elif self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAdmin, IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RegisterGetSerializer
        else:
            return RegisterSerializer

    def create(self, request):
        try:
            data = request.data
            serializer = UserRegisterSerializer(data=data)
            if serializer.is_valid():
                if CustomUser.objects.filter(email=data['email']).exists():
                    context = {
                        'message': 'Email already exists'
                    }
                    return Response(context, status=status.HTTP_400_BAD_REQUEST)

                if CustomUser.objects.filter(username=data['username']).exists():
                    context = {
                        'message': 'Username already exists'
                    }
                    return Response(context, status=status.HTTP_400_BAD_REQUEST)

                if data['password'] != data['confirm_password']:
                    context = {
                        'message': 'Passwords do not match'
                    }
                    return Response(context, status=status.HTTP_400_BAD_REQUEST)

                user = CustomUser.objects.create(

                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    username=data['username'].replace(" ", ""),
                    email=data['email'],
                    password=data['password'],
                    role = data['role'],
                    company = serializer.validated_data['company']
                )
                user.set_password(data['password'])
                if not request.data.get('email_verify'):
                    email = serializer.validated_data['email']
                    password = serializer.validated_data['password']
                    from_email = EMAIL_HOST_USER
                    to_email = [email]
                    token = str(uuid.uuid4())
                    decodeId = StringEncoder.encode(self, user.id)
                    subject = "User registered"
                    message = "User registered"
                    htmlMessage = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\
                                        <html xmlns="http://www.w3.org/1999/xhtml">\
                                        <head>\
                                            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\
                                            <title>Mongo DB</title>\
                                            <meta name="viewport" content="width=device-width, initial-scale=1.0" /> </head>\
                                        <body style="margin: 0; padding: 0; background: #eee;">\
                                            <div style="background: rgba(36, 114, 252, 0.06) !important;">\
                                            <table style="font: Arial, sans-serif; border-collapse: collapse; width:600px; margin: 0 auto;" width="600" cellpadding="0" cellspacing="0">\
                                                <tbody>\
                                                <tr>\
                                                    <td style="width: 100%; margin: 36px 0 0;">\
                                                    <div style="padding: 34px 44px; border-radius: 8px !important; background: #fff; border: 1px solid #dddddd5e; margin-bottom: 50px; margin-top: 50px;">\
                                                        <div class="email-logo">\
                                                        </div>\
                                                        <a href="#"></a>\
                                                        <div class="welcome-text">\
                                                        <h1 style="font:24px;"> Welcome <span class="welcome-hand">👋</span>\
                                                        </h1>\
                                                        </div>\
                                                        <div class="welcome-paragraph">\
                                                        <div style="padding: 20px 0px; font-size:16px; color: #384860;">Welcome to Saasot </div>\
                                                        <div style="padding:10px 0px; font-size: 16px; color: #384860;">Below is your account detail:<br />\
                                                        <p> ' + 'Email: ' + email + '</p>\
                                                        <p> ' + 'Password: ' + password + '</p></div>\
                                                        <div style="padding:10px 0px; font-size: 16px; color: #384860;">Please confirm your email<br />\
                                                        </div>\
                                                        <div style="padding-top:40px; cursor: pointer !important;" class="confirm-email-button">\
                                                        <a href=' + FRONTEND_SITE_URL + '/verify-email/' + decodeId + '/' + token + '/'' style="cursor: pointer;">\
                                                            <button style="height: 56px;padding: 15px 44px; background: #2472fc; border-radius: 8px;border-style: none; color: white; font-size: 16px; cursor: pointer !important;">Confirm Email</button>\
                                                        </a>\
                                                        </div>\
                                                        <div style="padding: 20px 0px; font-size: 16px; color: #384860;"> Sincerely, <br />The Saasot Team </div>\
                                                        </div>\
                                                        <div style="padding: 50px 0px;" class="email-bottom-para">\
                                                        <div style="padding: 20px 0px; font-size:16px; color: #384860;">This email was sent by Saasot . If you&#x27;d rather not receive this kind of email, Don’t want any more emails from Saasot? <a href="#">\
                                                            <span style="text-decoration:underline;"></span>\
                                                            </a>\
                                                        </div>\
                                                        <div style="font-size: 16px;color: #384860;"> © 2023 Saasot</div>\
                                                        </div>\
                                                    </div>\
                                                    </td>\
                                                </tr>\
                                                </tbody>\
                                            </table>\
                                            </div>\
                                        </body>\
                                        </html>'

                    data = send_mail(subject, message, from_email, to_email, html_message=htmlMessage)
                    user.forget_password_token = token
                else:
                    user.email_verified = True
                user.save()
                return Response({'message': 'User Registered Successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response({'message': f'{e} is required'}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        try:
            data = request.data
            # data['email_verified'] = False
            user = self.get_object()
            user.email_verified = False
            if request.data.get('email'):
                serializer = RegisterUpdateSerializer(user, data=data)
                if serializer.is_valid():
                    serializer.save()
                    email = serializer.data['email']
                    password = serializer.data['password']
                    from_email = EMAIL_HOST_USER
                    to_email = [email]
                    token = str(uuid.uuid4())
                    decodeId = StringEncoder.encode(self, user.id)
                    subject = "User registered"
                    message = "User registered"
                    htmlMessage = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\
                                        <html xmlns="http://www.w3.org/1999/xhtml">\
                                        <head>\
                                            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\
                                            <title>Mongo DB</title>\
                                            <meta name="viewport" content="width=device-width, initial-scale=1.0" /> </head>\
                                        <body style="margin: 0; padding: 0; background: #eee;">\
                                            <div style="background: rgba(36, 114, 252, 0.06) !important;">\
                                            <table style="font: Arial, sans-serif; border-collapse: collapse; width:600px; margin: 0 auto;" width="600" cellpadding="0" cellspacing="0">\
                                                <tbody>\
                                                <tr>\
                                                    <td style="width: 100%; margin: 36px 0 0;">\
                                                    <div style="padding: 34px 44px; border-radius: 8px !important; background: #fff; border: 1px solid #dddddd5e; margin-bottom: 50px; margin-top: 50px;">\
                                                        <div class="email-logo">\
                                                        </div>\
                                                        <a href="#"></a>\
                                                        <div class="welcome-text">\
                                                        <h1 style="font:24px;"> Welcome <span class="welcome-hand">👋</span>\
                                                        </h1>\
                                                        </div>\
                                                        <div class="welcome-paragraph">\
                                                        <div style="padding: 20px 0px; font-size:16px; color: #384860;">Welcome to Saasot </div>\
                                                        <div style="padding:10px 0px; font-size: 16px; color: #384860;">Below is your account detail:<br />\
                                                        <p> ' + 'Email: ' + email + '</p>\
                                                        <p> ' + 'Password: ' + password + '</p></div>\
                                                        <div style="padding:10px 0px; font-size: 16px; color: #384860;">Please confirm your email<br />\
                                                        </div>\
                                                        <div style="padding-top:40px; cursor: pointer !important;" class="confirm-email-button">\
                                                        <a href=' + FRONTEND_SITE_URL + '/verify-email/' + decodeId + '/' + token + '/'' style="cursor: pointer;">\
                                                            <button style="height: 56px;padding: 15px 44px; background: #2472fc; border-radius: 8px;border-style: none; color: white; font-size: 16px; cursor: pointer !important;">Confirm Email</button>\
                                                        </a>\
                                                        </div>\
                                                        <div style="padding: 20px 0px; font-size: 16px; color: #384860;"> Sincerely, <br />The Saasot Team </div>\
                                                        </div>\
                                                        <div style="padding: 50px 0px;" class="email-bottom-para">\
                                                        <div style="padding: 20px 0px; font-size:16px; color: #384860;">This email was sent by Saasot . If you&#x27;d rather not receive this kind of email, Don’t want any more emails from Saasot? <a href="#">\
                                                            <span style="text-decoration:underline;"></span>\
                                                            </a>\
                                                        </div>\
                                                        <div style="font-size: 16px;color: #384860;"> © 2023 Saasot</div>\
                                                        </div>\
                                                    </div>\
                                                    </td>\
                                                </tr>\
                                                </tbody>\
                                            </table>\
                                            </div>\
                                        </body>\
                                        </html>'

                    data = send_mail(subject, message, from_email, to_email, html_message=htmlMessage)
                    user.forget_password_token = token
                    user.save()
                    return Response({'message': 'User Updated Successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = RegisterUpdateSerializer(user, data=data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response({'message': f'{e} is required'}, status=status.HTTP_400_BAD_REQUEST)


class RegistrationCompanyUserView(APIView):
    serializer_class = RegisterSerializer
   
    def post(self, request):
        try:
            data = request.data.copy()
            company_name = data.pop('company', None)
            if company_name:
                existing_company = Company.objects.filter(name=company_name).first()
                if existing_company:
                    context = {
                        'message': 'Company with this name already exists'
                    }
                    return Response(context, status=status.HTTP_400_BAD_REQUEST)
                
                company_serializer = CompanySerializer(data={'name': company_name}) 
                # company_serializer = CompanySerializer(data = company_name)
                if company_serializer.is_valid():
                    company_instance = company_serializer.save()
                    data['company'] = company_instance.id
                    # company_serializer.save()
                    # data['company'] = company_serializer.instance.id
                else:
                    return Response({"message": "something wrong with company data"}, status=status.HTTP_400_BAD_REQUEST)
                # data['company'] = company_serializer.data['id']
            # data['role'] = 1
            serializer = RegisterSerializer(data=data)
            if serializer.is_valid():
                if CustomUser.objects.filter(email=data['email']).exists():
                    context = {
                        'message': 'Email already exists'
                    }
                    return Response(context, status=status.HTTP_400_BAD_REQUEST)

                if CustomUser.objects.filter(username=data['username']).exists():
                    context = {
                        'message': 'Username already exists'
                    }
                    return Response(context, status=status.HTTP_400_BAD_REQUEST)

                if data['password'] != data['confirm_password']:
                    context = {
                        'message': 'Passwords do not match'
                    }
                    return Response(context, status=status.HTTP_400_BAD_REQUEST)

                user = CustomUser.objects.create(
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    username=data['username'].replace(" ", ""),
                    email=data['email'],
                    password=data['password'],
                    role = data['role'],
                    company_id=data.get('company', None),
                    is_true=data.get('is_true', False)
                )
                user.set_password(data['password'])
                if not request.data.get('email_verify'):
                    email = serializer.validated_data['email']
                    password = serializer.validated_data['password']
                    from_email = EMAIL_HOST_USER
                    to_email = [email]
                    token = str(uuid.uuid4())
                    decodeId = StringEncoder.encode(self, user.id)
                    subject = "User registered"
                    message = "User registered"
                    htmlMessage = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\
                                        <html xmlns="http://www.w3.org/1999/xhtml">\
                                        <head>\
                                            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\
                                            <title>Mongo DB</title>\
                                            <meta name="viewport" content="width=device-width, initial-scale=1.0" /> </head>\
                                        <body style="margin: 0; padding: 0; background: #eee;">\
                                            <div style="background: rgba(36, 114, 252, 0.06) !important;">\
                                            <table style="font: Arial, sans-serif; border-collapse: collapse; width:600px; margin: 0 auto;" width="600" cellpadding="0" cellspacing="0">\
                                                <tbody>\
                                                <tr>\
                                                    <td style="width: 100%; margin: 36px 0 0;">\
                                                    <div style="padding: 34px 44px; border-radius: 8px !important; background: #fff; border: 1px solid #dddddd5e; margin-bottom: 50px; margin-top: 50px;">\
                                                        <div class="email-logo">\
                                                        </div>\
                                                        <a href="#"></a>\
                                                        <div class="welcome-text">\
                                                        <h1 style="font:24px;"> Welcome <span class="welcome-hand">👋</span>\
                                                        </h1>\
                                                        </div>\
                                                        <div class="welcome-paragraph">\
                                                        <div style="padding: 20px 0px; font-size:16px; color: #384860;">Welcome to Saasot </div>\
                                                        <div style="padding:10px 0px; font-size: 16px; color: #384860;">Below is your account detail:<br />\
                                                        <p> ' + 'Email: ' + email + '</p>\
                                                        <p> ' + 'Password: ' + password + '</p></div>\
                                                        <div style="padding:10px 0px; font-size: 16px; color: #384860;">Please confirm your email<br />\
                                                        </div>\
                                                        <div style="padding-top:40px; cursor: pointer !important;" class="confirm-email-button">\
                                                        <a href=' + FRONTEND_SITE_URL + '/verify-email/' + decodeId + '/' + token + '/'' style="cursor: pointer;">\
                                                            <button style="height: 56px;padding: 15px 44px; background: #2472fc; border-radius: 8px;border-style: none; color: white; font-size: 16px; cursor: pointer !important;">Confirm Email</button>\
                                                        </a>\
                                                        </div>\
                                                        <div style="padding: 20px 0px; font-size: 16px; color: #384860;"> Sincerely, <br />The Saasot Team </div>\
                                                        </div>\
                                                        <div style="padding: 50px 0px;" class="email-bottom-para">\
                                                        <div style="padding: 20px 0px; font-size:16px; color: #384860;">This email was sent by Saasot . If you&#x27;d rather not receive this kind of email, Don’t want any more emails from Saasot? <a href="#">\
                                                            <span style="text-decoration:underline;"></span>\
                                                            </a>\
                                                        </div>\
                                                        <div style="font-size: 16px;color: #384860;"> © 2023 Saasot</div>\
                                                        </div>\
                                                    </div>\
                                                    </td>\
                                                </tr>\
                                                </tbody>\
                                            </table>\
                                            </div>\
                                        </body>\
                                        </html>'

                    data = send_mail(subject, message, from_email, to_email, html_message=htmlMessage)
                    user.forget_password_token = token
                else:
                    user.email_verified = True
                user.save()
                return Response({'message': 'User Registered Successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response({'message': f'{e} is required'}, status=status.HTTP_400_BAD_REQUEST)




class VerifyEmail(APIView):
    lookup_url_kwarg = "token"
    lookup_url_kwarg2 = "uid"

    def get(self, request, *args, **kwargs):
        token = self.kwargs.get(self.lookup_url_kwarg)
        uid = self.kwargs.get(self.lookup_url_kwarg2)
        encoded_id = int(StringEncoder.decode(self, uid))
        print(token,"-------------",uid,"+++++++++++++++++++++++++++++++++",encoded_id)
        try:
            user_data = CustomUser.objects.filter(id=encoded_id, email_verified=False, forget_password_token=token)
        except:
            return Response("user does not found")
        print(user_data,"======================")
        if user_data:
            user_data.update(email_verified=True)
            context = {'message': 'Your email have been confirmed', 'status': status.HTTP_200_OK, 'error': False}
            return Response(context, status=status.HTTP_201_CREATED)
        print(user_data,"++++++++++")
        context = {
            'message': "Something went wrong!",
            'error': True
        }
        return Response(context, status=status.HTTP_400_BAD_REQUEST)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class LoginView(GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        
        email = request.data['email']
        password = request.data['password']
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            user = CustomUser.objects.filter(username=email).first()

        if user is None:
            context = {
                'message': 'Please enter valid login details'
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            context = {
                'message': 'Please enter valid login details'
            }

            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        if user.email_verified == False:
            context = {
                'message': 'Please confirm your email to access your account'
            }
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
            # CustomUser.objects.filter(id=request.user.id).update(is_inactive=False)

        useremail = user.email

        token = get_tokens_for_user(user)
        response = Response(status=status.HTTP_200_OK)

        # Set Token Cookie

        response.set_cookie(key='token', value=token, httponly=True)
        # cache.set('token', token, 60)
        if user.role ==  4:
            response.data = {
                'message': "Login Success",
                "user": {
                    "user_id": user.id,
                    "name": user.username,
                    'email': useremail,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'is_true': user.is_true
                    
                },
                'token': token['access'],
                'refresh': token['refresh']
            }
        else:
            response.data = {
                'message': "Login Success",
                "user": {
                    "user_id": user.id,
                    "name": user.username,
                    'email': useremail,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'company_id': user.company.id,
                    'company_name': user.company.name
                    
                },
                'token': token['access'],
                'refresh': token['refresh']
            }
        login(request, user, backend='authentication.authentication.EmailBackend')
        print(request.user,"---------------------------------------------")
        # request.user = user
        return response
        

# class ForgetPassword(APIView):
#     serializer_class = SendForgotEmailSerializer

#     def post(self, request):
#         protocol = request.scheme
#         domain = FRONTEND_SITE_URL
#         # domain = request.get_host()
#         email = request.data
#         serializer = SendForgotEmailSerializer(data=email)
#         if serializer.is_valid(raise_exception=True):
#             email = request.data['email']
#             user = CustomUser.objects.filter(email=email).first()
#             if not user:
#                 user = CustomUser.objects.filter(username=email).first()
#                 return Response({'message': 'Email does not exists in database'}, status=status.HTTP_400_BAD_REQUEST)
#             if  user and not user.email_verified:
#                 return Response({'message': 'Please confirm your email to access your account'}, status=status.HTTP_400_BAD_REQUEST)
#             token = str(uuid.uuid4())
#             token_expire_time = datetime.utcnow() + timedelta(minutes=3)
#             user.token_expire_time = token_expire_time
#             user.forget_password_token = token
#             user.save()
#             user_id = user.id
#             email_from = EMAIL_HOST_USER
#             subject = 'Forgot Password Email'
#             message = "\n\n\n\nHI " + str(user.username) + " \n\n link to reset password is :" +str(domain) + "/password-reset/" + str(token) + "/" + str(user_id)
#             restUrl =  str(domain)+"/reset-password/" + str(token) + "/" + str(user_id)+"/"
#             print(restUrl,'restUrlrestUrl')

#             htmlMessage = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\
#                         <html xmlns="http://www.w3.org/1999/xhtml">\
#                         <head>\
#                             <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\
#                             <title>Mongo DB</title>\
#                             <meta name="viewport" content="width=device-width, initial-scale=1.0" /> </head>\
#                         <body style="margin: 0; padding: 0; background: #eee;">\
#                             <div style="background: rgba(36, 114, 252, 0.06) !important;">\
#                             <table style="font: Arial, sans-serif; border-collapse: collapse; width:600px; margin: 0 auto;" width="600" cellpadding="0" cellspacing="0">\
#                                 <tbody>\
#                                 <tr>\
#                                     <td style="width: 100%; margin: 36px 0 0;">\
#                                     <div style="padding: 34px 44px; border-radius: 8px !important; background: #fff; border: 1px solid #dddddd5e; margin-bottom: 50px; margin-top: 50px;">\
#                                         <div class="email-logo">\
#                                         <img style="width: 165px;" src="http://122.160.74.251:3004/MN big.png" />\
#                                         </div>\
#                                         <a href="#"></a>\
#                                         <div class="welcome-text">\
#                                         <h1 style="font:24px;"> Welcome <span class="welcome-hand">👋</span>\
#                                         </h1>\
#                                         </div>\
#                                         <div class="welcome-paragraph">\
#                                         <div style="padding: 20px 0px; font-size:16px; color: #384860;">Welcome to Note Taking App !</div>\
#                                         <div style="padding:10px 0px; font-size: 16px; color: #384860;">Please click the button below to Reset your Password. <br />\
#                                         </div>\
#                                         <div style="padding: 20px 0px; font-size: 16px; color: #384860;"> Sincerely, <br />Note Taking App Team </div>\
#                                         </div>\
#                                         <div style="padding-top:40px; cursor: pointer !important;" class="confirm-email-button">\
#                                         <a href="'+restUrl+'" style="cursor: pointer;">\
#                                             <button style="height: 56px;padding: 15px 44px; background: #2472fc; border-radius: 8px;border-style: none; color: white; font-size: 16px; cursor: pointer !important;">Reset Password</button>\
#                                         </a>\
#                                         </div>\
#                                         <div style="padding: 50px 0px;" class="email-bottom-para">\
#                                         <div style="padding: 20px 0px; font-size:16px; color: #384860;">This email was sent by Note Taking App. If you&#x27;d rather not receive this kind of email, Don’t want any more emails from Note Taking App ? <a href="#">\
#                                             <span style="text-decoration:underline;"></span>\
#                                             </a>\
#                                         </div>\
#                                         <div style="font-size: 16px;color: #384860;"> © 2023 Note Taking App </div>\
#                                         </div>\
#                                     </div>\
#                                     </td>\
#                                 </tr>\
#                                 </tbody>\
#                             </table>\
#                             </div>\
#                         </body>\
#                         </html>'
#             try:
#                 send_mail(subject,message, email_from,[email], html_message=htmlMessage, fail_silently=False,)
#                 return Response({'message': 'Email Send Successfully, Please check your email'},status=status.HTTP_200_OK)      
#             except Exception as e:
#                 pass
#         else:
#             return Response({'message': 'There is an error to sending the data'},status=status.HTTP_400_BAD_REQUEST)



class ForgetPassword(APIView):
    serializer_class = SendForgotEmailSerializer

    def post(self, request):
        urlObject = request._current_scheme_host
        email = request.data
        serializer = SendForgotEmailSerializer(data=email)
        if serializer.is_valid(raise_exception=True):
            email = request.data['email']
            user = CustomUser.objects.filter(email=email).first()
            if not user:
                user = CustomUser.objects.filter(username=email).first()
                return Response({'message': 'Email does not exists in database'}, status=status.HTTP_400_BAD_REQUEST)
            if not user.email_verified:
                context = {
                    'message': 'Please confirm your email to access your account'
                }
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
            token = str(uuid.uuid4())
            decodeId = StringEncoder.encode(self, user.id)
            token_expire_time = datetime.utcnow() + timedelta(minutes=3)
            user.forget_password_token = token
            user.token_expire_time = token_expire_time
            user.save()

            user_id = user.id
            email_from = EMAIL_HOST_USER
            subject = 'Forgot Password Email'
            message = "\n\n\n\nHI " + str(user.username) + " \n\n link to reset password is :" +str(FRONTEND_SITE_URL) + "/password-reset/" + str(token) + "/" + str(user_id)
            restUrl =  str(FRONTEND_SITE_URL)+"/reset-password/" + str(token) + "/" + str(decodeId)+"/"
            print(restUrl,'restUrlrestUrl')

            htmlMessage = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\
                        <html xmlns="http://www.w3.org/1999/xhtml">\
                        <head>\
                            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\
                            <title>Mongo DB</title>\
                            <meta name="viewport" content="width=device-width, initial-scale=1.0" /> </head>\
                        <body style="margin: 0; padding: 0; background: #eee;">\
                            <div style="background: rgba(36, 114, 252, 0.06) !important;">\
                            <table style="font: Arial, sans-serif; border-collapse: collapse; width:600px; margin: 0 auto;" width="600" cellpadding="0" cellspacing="0">\
                                <tbody>\
                                <tr>\
                                    <td style="width: 100%; margin: 36px 0 0;">\
                                    <div style="padding: 34px 44px; border-radius: 8px !important; background: #fff; border: 1px solid #dddddd5e; margin-bottom: 50px; margin-top: 50px;">\
                                        <div class="email-logo">\
                                        <img style="width: 165px;" src="http://122.160.74.251:3004/MN big.png" />\
                                        </div>\
                                        <a href="#"></a>\
                                        <div class="welcome-text">\
                                        <h1 style="font:24px;"> Welcome <span class="welcome-hand">👋</span>\
                                        </h1>\
                                        </div>\
                                        <div class="welcome-paragraph">\
                                        <div style="padding: 20px 0px; font-size:16px; color: #384860;">Welcome to Note Taking App !</div>\
                                        <div style="padding:10px 0px; font-size: 16px; color: #384860;">Please click the button below to Reset your Password. <br />\
                                        </div>\
                                        <div style="padding: 20px 0px; font-size: 16px; color: #384860;"> Sincerely, <br />Note Taking App Team </div>\
                                        </div>\
                                        <div style="padding-top:40px; cursor: pointer !important;" class="confirm-email-button">\
                                        <a href="'+restUrl+'" style="cursor: pointer;">\
                                            <button style="height: 56px;padding: 15px 44px; background: #2472fc; border-radius: 8px;border-style: none; color: white; font-size: 16px; cursor: pointer !important;">Reset Password</button>\
                                        </a>\
                                        </div>\
                                        <div style="padding: 50px 0px;" class="email-bottom-para">\
                                        <div style="padding: 20px 0px; font-size:16px; color: #384860;">This email was sent by Note Taking App. If you&#x27;d rather not receive this kind of email, Don’t want any more emails from Note Taking App ? <a href="#">\
                                            <span style="text-decoration:underline;"></span>\
                                            </a>\
                                        </div>\
                                        <div style="font-size: 16px;color: #384860;"> © 2023 Note Taking App </div>\
                                        </div>\
                                    </div>\
                                    </td>\
                                </tr>\
                                </tbody>\
                            </table>\
                            </div>\
                        </body>\
                        </html>'
            try:
                send_mail(subject,message, email_from,[email], html_message=htmlMessage, fail_silently=False,)
                return Response({'message': 'Email Send Successfully, Please check your email'},status=status.HTTP_200_OK)      
            except Exception as e:
                pass
        else:
            return Response({'message': 'There is an error to sending the data'},status=status.HTTP_400_BAD_REQUEST)




# class ResetPassword(APIView):
#     serializer_class = ChangePasswordSerializer
#     lookup_url_kwarg = "token"
#     lookup_url_kwarg2 = "uid"

#     def get(self, request, args, *kwargs):
#         serializer_class = ChangePasswordSerializer
#         token = self.kwargs.get(self.lookup_url_kwarg)
#         uid = self.kwargs.get(self.lookup_url_kwarg2)
#         user_data = CustomUser.objects.filter(id=uid).first()
#         if not user_data.forget_password_token:
#             return Response({'token_expire': 'Token Expired'}, status=status.HTTP_400_BAD_REQUEST)
#         if token != user_data.forget_password_token:
#             return Response({'token_expire': 'Token Expired'}, status=status.HTTP_400_BAD_REQUEST)

#         token_expire_time = user_data.token_expire_time.replace(tzinfo=None)
#         current_expire_time = datetime.datetime.utcnow()
#         if current_expire_time > token_expire_time:
#             return Response({'token_expire': 'Token Expired'}, status=status.HTTP_400_BAD_REQUEST)

#         context = {
#             'token_expire_time': token_expire_time
#             # 'current_expire_time': current_expire_time
#         }
#         response = Response(context, status=status.HTTP_200_OK)
#         return response

    
#     def put(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         password = request.data['password']
#         print()
#         confirm_password = request.data['confirm_password']

#         if password != confirm_password:
#             return Response({'message': 'Password and Confirm Password do not match'},status=status.HTTP_400_BAD_REQUEST)
#         user_id = self.kwargs.get(self.lookup_url_kwarg2)
#         user_data = CustomUser.objects.get(id=user_id)
#         user_data.set_password(password)
#         user_data.forget_password_token = None
#         user_data.save()
#         if user_data != 0:
#             return Response({'message': 'Your Password updated Successfully'}, status=status.HTTP_200_OK)
#         else:
#             return Response({'message': 'There is an error to updating the data'}, status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    lookup_url_kwarg = "token"
    lookup_url_kwarg2 = "uid"

    def get(self, request, *args, **kwargs):
        token = self.kwargs.get(self.lookup_url_kwarg)
        uid = self.kwargs.get(self.lookup_url_kwarg2)
        encoded_id = int(StringEncoder.decode(self, uid))
        user_data = CustomUser.objects.filter(id=encoded_id).first()
        if not user_data.forget_password_token:
            return Response({'token_expire': 'Token Expired'}, status=status.HTTP_400_BAD_REQUEST)
        if token != user_data.forget_password_token:
            return Response({'token_expire': 'Token Expired'}, status=status.HTTP_400_BAD_REQUEST)
        token_expire_time = user_data.token_expire_time.replace(tzinfo=None)
        current_expire_time = datetime.datetime.utcnow()
        if current_expire_time > token_expire_time:
            return Response({'token_expire': 'Token Expired'}, status=status.HTTP_400_BAD_REQUEST)

        context = {
            'token_expire_time': token_expire_time,
            'current_expire_time': current_expire_time
        }
        response = Response(context, status=status.HTTP_200_OK)
        return response

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data = serializer.validated_data
        password = request.data['password']
        confirm_password = request.data['confirm_password']

        if len(password) < 7 or len(confirm_password) < 7:
            return Response({'message': 'Make sure your password is at lest 7 letters'},
                            status=status.HTTP_400_BAD_REQUEST)

        if password != confirm_password:
            return Response({'message': 'Password and Confirm Password do not match'},
                            status=status.HTTP_400_BAD_REQUEST)

        user_id = int(StringEncoder.decode(self, self.kwargs.get(self.lookup_url_kwarg2)))
        user_data = CustomUser.objects.get(id=user_id)
        user_data.set_password(password)
        user_data.forget_password_token = None
        user_data.save()
        if user_data != 0:
            return Response({'message': 'Your Password updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'There is an error to updating the data'}, status=status.HTTP_400_BAD_REQUEST)
    






# __________________________code_by_davinder_rajput___________________________________________________________________
from rest_framework import generics   
from .serializers import  GetAllUserRoleSerializer

     
class UserByRoleAPIView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = GetAllUserRoleSerializer
    lookup_field = 'id'   

    def get_queryset(self):
        user_id = self.kwargs.get('id')
        return CustomUser.objects.filter(id=user_id).prefetch_related('transactions')  





class UserUpdateViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserUpdateSerializer


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    # def perform_update(self, serializer):
    #     company_name = self.request.data.get('company[name]')

    #     if company_name:
    #         # Check if company with the provided name already exists
    #         if Company.objects.filter(name=company_name).exists():
    #             return Response({'message': 'Company with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST) 
            
    #         else:
    #             try:
    #                 company_instance = serializer.instance.company
    #                 company_instance.name = company_name
    #                 company_instance.save()
    #             except Exception as e:
    #                 print(f"Error updating company: {e}")
    #     else:
    #         print("Company name not provided in the request.")
    #     serializer.save()
    
    # def perform_update(self, serializer):
    #     company_name = self.request.data.get('company[name]')

    #     if company_name:
    #         try:
    #             company_instance = serializer.instance.company
    #             company_instance.name = company_name
    #             company_instance.save()
    #         except Exception as e:
    #             print(f"Error updating company: {e}")
    #     else:
    #         print("Company ID not provided in the request.")
    #     serializer.save()

    # def perform_update(self, serializer):
    #     serializer.save()



# =================prince ========================
        
class UserListView(generics.ListAPIView):
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        role = self.request.query_params.get('role')  # Get the role from the query parameters
        if role:
            return CustomUser.objects.filter(role=role)
        else:
            return CustomUser.objects.all()



    

   
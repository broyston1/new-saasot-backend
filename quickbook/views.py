from intuitlib.client import AuthClient
from intuitlib.migration import migrate
from intuitlib.enums import Scopes
from intuitlib.exceptions import AuthClientError

# from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.conf import settings
# from django.core import serializers



import json
import datetime

from django.core.exceptions import ObjectDoesNotExist

from rest_framework.response import Response
from rest_framework import status, viewsets, mixins, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import QuickBooksToken
from .refresh_token import refresh_token_function
from .services import qbo_api_call, product_sync


# Create your views here.
def index(request):
    return render(request, 'index.html')

class QuickbookOauth(APIView):
    """
    A viewset that provides the oauth login page url.
    """
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            auth_client = AuthClient(
                settings.CLIENT_ID, 
                settings.CLIENT_SECRET, 
                settings.REDIRECT_URI, 
                settings.ENVIRONMENT,
            )
            url = auth_client.get_authorization_url([Scopes.ACCOUNTING])
            print("iiiiiiiiiiiiiiiiiiiiiiii",url)
            request.session['state'] = auth_client.state_token
            return Response({"url":url, "state_token":  auth_client.state_token}, status=status.HTTP_200_OK)
        except AuthClientError as e:
            print(e.status_code)
            print(e.content)
            print(e.intuit_tid)
        except Exception as e:
            print(e)
            return Response({"sds":"dsdsd"})

# def openid(request):
#     auth_client = AuthClient(
#         settings.CLIENT_ID, 
#         settings.CLIENT_SECRET, 
#         settings.REDIRECT_URI, 
#         settings.ENVIRONMENT,
#     )

#     url = auth_client.get_authorization_url([Scopes.OPENID, Scopes.EMAIL])
#     request.session['state'] = auth_client.state_token
#     return redirect(url)

class QuickbookCallback(APIView):
    """
    A viewset reterive the acess_token and refersh_token.
    """
    
    def get(self, request):
        auth_client = AuthClient(
            settings.CLIENT_ID, 
            settings.CLIENT_SECRET, 
            settings.REDIRECT_URI, 
            settings.ENVIRONMENT, 
            state_token=request.session.get('state', None),
        )

        state_tok = request.GET.get('state', None)
        print("oooooooooooooooo",state_tok)
        error = request.GET.get('error', None)
        
        # if error == 'access_denied':
        #     return redirect('app:index')
        
        if state_tok is None:
            return HttpResponseBadRequest()
        elif state_tok != auth_client.state_token:  
            return HttpResponse('unauthorized', status=401)
        
        auth_code = request.GET.get('code', None)
        realm_id = request.GET.get('realmId', None)
        request.session['realm_id'] = realm_id

        if auth_code is None:
            return Response({"msg": "bad request"})

        try:
            auth_client.get_bearer_token(auth_code, realm_id=realm_id)
            request.session['access_token'] = auth_client.access_token
            request.session['refresh_token'] = auth_client.refresh_token
            request.session['id_token'] = auth_client.id_token
            
            expires_in = auth_client.expires_in

            expires_at = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
            expires_at_str = expires_at.isoformat()

            QuickBooksToken.objects.create(
            access_token=auth_client.access_token,
            refresh_token=auth_client.refresh_token,
            realm_id = realm_id,
            expires_at= expires_at_str
        )
            return Response({"msg": 'app:connected'})
        except AuthClientError as e:
            # just printing status_code here but it can be used for retry workflows, etc
            print(e.status_code)
            print(e.content)
            print(e.intuit_tid)
            return Response({"msg": e.status_code})
        # except Exception as e:
        #     print(e)
        # return Response({"msg": 'app:connected'})
    

# def connected(request):
#     auth_client = AuthClient(
#         settings.CLIENT_ID, 
#         settings.CLIENT_SECRET, 
#         settings.REDIRECT_URI, 
#         settings.ENVIRONMENT, 
#         access_token=request.session.get('access_token', None), 
#         refresh_token=request.session.get('refresh_token', None), 
#         id_token=request.session.get('id_token', None),
#     )

#     if auth_client.id_token is not None:
#         return render(request, 'connected.html', context={'openid': True})
#     else:
#         return render(request, 'connected.html', context={'openid': False})

class SyncInvoice(APIView):

    # permission_classes = [IsAuthenticated]

    def get(self, request):
        q_b = QuickBooksToken.objects.all().first()
        auth_client = AuthClient(
            settings.CLIENT_ID, 
            settings.CLIENT_SECRET, 
            settings.REDIRECT_URI, 
            settings.ENVIRONMENT, 
            access_token=q_b.access_token,
            refresh_token=q_b.refresh_token,
            realm_id=q_b.realm_id
        )

        if auth_client.access_token is not None:
            access_token = auth_client.access_token
      
        if auth_client.realm_id is None:
            raise ValueError('Realm id not specified.')
        
        res = refresh_token_function(q_b.refresh_token)
        q_b.access_token = res['access_token']
        q_b.refresh_token = res['refresh_token']
        q_b.save()
        response = qbo_api_call(q_b.access_token, q_b.realm_id)
        
        if not response.ok:
            print(response.status_code, response, "=-=-=-=-")
            # return Response({"message": ' '.join([response.content, str(response.status_code)])})
            return Response({"message": response})
        else:
            print(response.content, "=-=-=-=-=-=---=--=-=-")
            return Response({"message": response.content})

class SyncProduct(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        q_b = QuickBooksToken.objects.all().first()
        auth_client = AuthClient(
            settings.CLIENT_ID, 
            settings.CLIENT_SECRET, 
            settings.REDIRECT_URI, 
            settings.ENVIRONMENT, 
            access_token=q_b.access_token,
            refresh_token=q_b.refresh_token,
            realm_id=q_b.realm_id
        )

        if auth_client.access_token is not None:
            access_token = auth_client.access_token
    
        if auth_client.realm_id is None:
            raise ValueError('Realm id not specified.')
        
        res = refresh_token_function(q_b.refresh_token)
        q_b.access_token = res['access_token']
        q_b.refresh_token = res['refresh_token']
        q_b.save()
        response = product_sync(q_b.access_token, q_b.realm_id, self.request.user)
        
        if not response.ok:
            print(response.status_code, response, "=-=-=-=-")
            # return Response({"message": ' '.join([response.content, str(response.status_code)])})
            return Response({"message": response})
        else:
            return Response({"message": response.content})

class Disconnect(APIView):
    def get(self, request):
        QuickBooksToken.objects.all().delete()
        return Response({"message": "Sucessfully Disconnected"})

class CheckQuickbookConnectivity(APIView):

    def get(self, request):
        q_b = QuickBooksToken.objects.all()
        if len(q_b)<1:
            return Response({"message": "Disconnected"})
        else:
            return Response({"message": "Connected"})

import requests
from django.conf import settings
from .retrive_data import*

def qbo_api_call(access_token, realm_id):
    """[summary]
    
    """
    
    if settings.ENVIRONMENT == 'production':
        base_url = settings.QBO_BASE_PROD
    else:
        base_url =  settings.QBO_BASE_SANDBOX

    # route = '/v3/company/{0}/companyinfo/{0}'.format(realm_id)
    route = f'/v3/company/{realm_id}/query'
    auth_header = 'Bearer {0}'.format(access_token)
    query = "SELECT * FROM Invoice"
    headers = {
        'Authorization': auth_header, 
        'Accept': 'application/json'
    }
    return requests.get('{0}{1}'.format(base_url, route), headers=headers, params={'query': query})


import requests
from django.conf import settings

def product_sync(access_token, realm_id, user):
    """
    [summary]
    """
    if settings.ENVIRONMENT == 'production':
        base_url = settings.QBO_BASE_PROD
    else:
        base_url =  settings.QBO_BASE_SANDBOX

    route = f"/v3/company/{realm_id}/query?query=SELECT * FROM Item"
    auth_header = 'Bearer {0}'.format(access_token)
    query = "SELECT * FROM Invoice"
    headers = {
        'Authorization': auth_header, 
        'Accept': 'application/json'
    }
    response = requests.get('{0}{1}'.format(base_url, route), headers=headers, params={'query': query})
    retrieve_product_data(response.content, user)
    return response


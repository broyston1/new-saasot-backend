
from django.test import TestCase

# Create your tests here.

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

# OAuth 2.0 credentials
client_id = 'AB5jriyrnJzbgjznrcPDWf69jzv73kxxi2gpNGrW39O88ESsDC'
client_secret = 'McGH62O81hsBwyoqRBCDnmkkp78eVV4mL7wfFD28'
redirect_uri = 'YOUR_REDIRECT_URI'  # This is typically not used for backend applications
scope = ['com.intuit.quickbooks.accounting']

# Initialize OAuth2Session
client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client, scope=scope)

# Fetch access token
token_url = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'
token = oauth.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret)

# Use the access token to make API requests
company_id = '9130357970048416'
api_url = f'https://quickbooks.api.intuit.com/v3/company/{company_id}/query?query=SELECT * FROM Invoice'
try:
    response = oauth.get(api_url)
    response.raise_for_status()  # Check for HTTP errors
    data = response.json()
    print(data)
except Exception as e:
    print("Error:", e)
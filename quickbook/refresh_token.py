import requests
from django.conf import settings

def refresh_token_function(refresh_token):
    refresh_url = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'

    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id':  settings.CLIENT_ID,
        'client_secret': settings.CLIENT_SECRET
    }

    response = requests.post(refresh_url, data=payload)

    if response.status_code == 200:
        response_data = response.json()
        new_access_token = response_data['access_token']
        new_refresh_token = response_data['refresh_token']
        return {"access_token": new_access_token, "refresh_token": new_refresh_token}
    else:
        # Handle error response
        return None, None

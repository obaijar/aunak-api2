# your_app/utils.py

import requests
from django.conf import settings
from .models import DropboxToken

def refresh_dropbox_token():
    url = "https://api.dropbox.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": settings.DROPBOX_REFRESH_TOKEN,
        "client_id": settings.DROPBOX_APP_KEY,
        "client_secret": settings.DROPBOX_APP_SECRET,
    }
    
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        new_token = response.json()['access_token']
        # Update the token in settings
        settings.DROPBOX_ACCESS_TOKEN = new_token
        # Update the token in the database
        token_instance, created = DropboxToken.objects.get_or_create(id=1)
        token_instance.access_token = new_token
        token_instance.save()
    else:
        raise Exception("Failed to refresh Dropbox token")

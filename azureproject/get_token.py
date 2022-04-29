import os
from azure.identity import DefaultAzureCredential
import django.conf as conf

def get_token():
    print("DJANGO_SETTINGS_MODULE = " + os.environ['DJANGO_SETTINGS_MODULE'])
    if 'IDENTITY_ENDPOINT' in os.environ:    
        print("IDENTITY_ENDPOINT = " + os.environ['IDENTITY_ENDPOINT'])
    if 'WEBSITE_HOSTNAME' in os.environ:        
        print("WEBSITE_HOSTNAME = " + os.environ['WEBSITE_HOSTNAME'])
        # Azure hosted, refresh token that becomes password.
        azure_credential = DefaultAzureCredential()
        # Get token for Azure Database for PostgreSQL
        token = azure_credential.get_token("https://ossrdbms-aad.database.windows.net")
        conf.settings.DATABASES['default']['PASSWORD'] = token.token
        print(DATABASES['default'])
    else:
        # Locally, read password from environment variable.
        conf.settings.DATABASES['default']['PASSWORD'] = os.environ['DBPASS']
        print("Read password env variable.")
    return
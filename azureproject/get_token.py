import os
from azure.identity import DefaultAzureCredential

def get_token():
    print("django_settings_module = " + os.environ['DJANGO_SETTINGS_MODULE'])
    if 'WEBSITE_HOSTNAME' in os.environ:        
        from azureproject.production import DATABASES
        # Azure hosted, refresh token that becomes password.
        azure_credential = DefaultAzureCredential()
        # Get token for Azure Database for PostgreSQL
        token = azure_credential.get_token("https://ossrdbms-aad.database.windows.net")
        DATABASES['default']['PASSWORD'] = token.token
        print("Token = " + token.token)
    else:
        # Locally, read password from environment variable.
        from azureproject.development import DATABASES
        DATABASES['default']['PASSWORD'] = os.environ['DBPASS']
        print("Read password env variable.")
    return
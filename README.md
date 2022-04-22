# Deploy a Python (Django) web app with PostgreSQL and Blob Storage in Azure

This is a Python web app using the Django framework with three Azure services: Azure App Service, Azure Database for PostgreSQL relational database service, and Azure Blob Storage. This app is designed to be be run locally and then deployed to Azure. 

| Function      | Local Dev | Azure Hosted |
| ------------- | --------- | ------------ |
| Web app | runs locally, e.g., http://127.0.0.1:8000 | runs in App Service, e.g., https://\<app-name>.azurewebsites.net  |
| Database | Local PostgreSQL instance | Azure PostgreSQL service |
| Storage | Azure Blob Storage* or local emulator like [Azurite emulator for local Azure storage development](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azurite) | Azure Blob Storage |


\*Current code assumes Azure Blob Storage used locally. To use Azurite, you would need to set STORAGE_ACCOUNT_NAME and STORAGE_CONTAINER_NAME variables appropriately in *.env* as well as add AZURITE_ACCOUNTS variable. Also would need to run Django on https, which would require a certificate and adding some libraries. Perhaps beyond the scope of this sample app.

The assumption is that code doesn't change when moving from dev to Azure-hosted. With that in mind, there are two patterns for dealing with authentication:

|   | Local dev | Azure-hosted |
| - | --------- | ------------ |
| pattern&nbsp;1 | app service principal <br> add AZURE_CLIENT_ID, AZURE_TENANT_ID, and AZURE_CLIENT_SECRET to the *.env* file | app service principal <br> configure app settings for AZURE_CLIENT_ID, AZURE_TENANT_ID, and AZURE_CLIENT_SECRET |
| pattern&nbsp;2 | AD group, developer account<br> login in with `az login` | managed identity<br> configure as shown in [Authentication Azure-hosted app to Azure resources](https://docs.microsoft.com/en-us/azure/developer/python/sdk/authentication-azure-hosted-apps) |

The code doesn't change between pattern 1 and 2, only what goes into *.env* file in local dev case. We are primarily interested in pattern 2 and showing that with managed identity in Azure.

See [Tip 7](#tip-7) below for a bit of gotcha using developer account.

Example screenshot:

![Example review list with images](/static/images/Example-reviews.png)

## Propagate Django changes

Propagate changes in restaurant review app back to previous Django tutorials, including:

* csrf token use, don't use exempt in views.py
* message passing to forms when there is an error (for add review and restaurant), see [views.py](./restaurant_review/views.py) for an example
* add check of forms looking for blank fields and raise error (for add review and restaurant)
* check render() lookup on url and make sure they are correct for error conditions, in some cases just use reverse()
* pull all CSS to [restaurants.css](./static/restaurant.css) and link to from base.html, should be no CSS in other templates

## Deployment

1. Do managed identity work following [Auth from Azure-hosted apps](https://review.docs.microsoft.com/en-us/azure/developer/python/sdk/authentication-azure-hosted-apps):
    * app service, set managed identity as system-assigned
    * assign role as "Storage Blob Data Contributor", so app service can connect to storage

1. Set up PostgreSQL
    * add firewall rule so local machine can connect (necessary if you are creating table in VS Code, otherwise optional)
    * "Allow public access from any Azure service" as we did in previous tutorial. **Can we use managed identity?** See [Tip 8](#tip-8---postgresql).

1. Deploy the app with one of the methods: VS Code, local git, ZIP.
    * set app service configuration variables for: DBNAME, DBHOST, DBUSER, DBPASS, STORAGE_ACCOUNT_NAME, STORAGE_CONTAINER_NAME
    * ssh into app service
    * create the databases with `python manage.py migrate`

## Requirements

The [requirements.txt](./requirements.txt) has the following packages:

| Package | Description |
| ------- | ----------- |
| [Django](https://pypi.org/project/Django/) | Web application framework. |
| [pyscopg2-binary](https://pypi.org/project/psycopg-binary/) | PostgreSQL database adapter for Python. |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Read key-value pairs from .env file and set them as environment variables. In this sample app, those variables describe how to connect to the database locally. <br><br> This package is used in the [manage.py](./manage.py) file to load environment variables. |
| [whitenoise](https://pypi.org/project/whitenoise/) | Static file serving for WSGI applications, used in the deployed app. <br><br> This package is used in the [azureproject/production.py](./azureproject/production.py) file, which configures production settings. |
| [azure-blob-storage](https://pypi.org/project/azure-storage/) | Microsoft Azure Storage SDK for Python |
| [azure-identity](https://pypi.org/project/azure-identity/) | Microsoft Azure Identity Library for Python |

## How to run (Windows)

Create a virtual environment.

```dos
py -m venv .venv
.venv/scripts/activate
```

Install the dependencies.

```dos
pip install -r requirements.txt
```

Create the `restaurant` and `review` tables.

```dos
python manage.py migrate
```

Run the app.

```dos
python manage.py runserver
```

## Tips for development (Windows)

### Tip 1

When making [model.py](./restaurant_review/models.py) changes run `python manage.py makemigrations` to pick up those changes. For more information, see [django-admin and manage.py](https://docs.djangoproject.com/en/4.0/ref/django-admin/#makemigrations). Run `python manage.py migrate` after `makemigrations`.

### Tip 2

When creating a new PostgreSQL locally, for example with [Azure Data Studio](https://docs.microsoft.com/en-us/sql/azure-data-studio/what-is-azure-data-studio?view=sql-server-ver15):

```dos
CREATE DATABASE <database-name>;
```

Or, with [psql.exe](https://www.postgresql.org/download/):

```dos
psql --username=<user-name> --password <password>

postgres=# CREATE DATABASE <database-name>;
postgres=# \c <database-name>
postgres=# \l
postgres=# \du
postgres=# \q
```

### Tip 3

To create an GUID in Python, use [UUIDField](https://docs.djangoproject.com/en/1.8/ref/models/fields/#uuidfield), which creates a universally unique identifier. When used with PostgreSQL, this stores in a **uuid** datatype.

```python
import uuid
from django.db import models

# model table column example
image_name = models.CharField(max_length=100, null=True)    

# create a uuid
uuid_str = str(uuid.uuid4()) 
```

CharField could be max length 32 (size of uuid) but doesn't hurt to make it bigger in case some other uuid that is longer is used.

### Tip 4

To work with the Python SDK and Azure Blob Storage, see [Quickstart: Manage blobs with Python v12 SDK](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python).

Create container called *restaurants* and set access level to *Blob (anonymous read access for blobs only)*. It makes this example easier to have images public when **reading**. Could set up the example so that images are accessed through web app and not public, but this would require more coding and would complicate the presentation.

When **writing**, this should be done authenticated. Locally with authenticated Azure AD User or App service principal (registered app) with role. Deployed, with App service principal or managed identity.

### Tip 5

To work with the HTML input file, make sure the form tag has *encytype*.

```html
<form method="POST" action="{% url 'add_review' restaurant.id %}" enctype="multipart/form-data">
    <label for="reviewImage" class="form-label">Add a photo</label>
    <input type="file" class="form-control" id="reviewImage" 
           name="reviewImage" accept="image/png, image/jpeg">                    
</form>
```

The input tag *accept* attribute only filters what can be uploaded in the upload dialog box. It can easily be circumvented by changing the filter. A more rigorous check would be to use a library like [Pillow](https://pillow.readthedocs.io/en/stable/) in Python, or do some other checking in JavaScript before upload. This is beyond the scope of this sample app.

### Tip 6

This sample app uses the Django [messages framework](https://docs.djangoproject.com/en/4.0/ref/contrib/messages/). For example, to pass a message back if there is an error in a form submission (add restaurant, add review), do this:

```python
messages.add_message(request, messages.INFO, 
    'Restaurant not added. Include at least a restaurant name and description.')
return HttpResponseRedirect(reverse('create_restaurant'))  
```

In the template redirected to put:

```html
{% if messages %}
<ul class="messages">
    {% for message in messages %}
    <li{% if message.tags %} class="{{ message.tags }}"{% endif %}>{{ message }}</li>
    {% endfor %}
</ul>
{% endif %}
```

The message backend is set in [settings.py](./azureproject/settings.py) and [production.py](./azureproject/production.py) with:

```python
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
```

This storage messages in session data. The default is cookie if the `MESSAGE_STORAGE` variable is not set.

### Tip 7

A big gotcha (that some may hit, I did) with using developer account in local dev is that you could get "SharedTokenCacheCredential: Azure Active Directory error '(invalid_grant) AADSTS500200" error even following instructions in how to use login in with developer account and `AzureDefaultCredential()`. After some looking around it seems that there can be problems with SharedTokenCacheCredential in Visual Studio and this is recommended:

```python
azure_credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
``` 
After doing that, I could sign in to Visual Studio code or use `az login` and my developer account worked. There looks to be a way to clear out your msal.cache but that seems extreme. References: [issue 16306](https://github.com/Azure/azure-sdk-for-net/issues/16306#issuecomment-724189313), [issue 16828](https://github.com/Azure/azure-sdk-for-python/issues/16828)

Another workaround, not recommended in general, is to just add to *.env* file AZURE_USERNAME and AZURE_PASSWORD to directly pass the values in. DefaultAzureCredential() without exclude flag will find the values in the *.env* file and use them.

Is there any harm on keeping `exclude_shared_token_cache_credential=True` when deploying?

### Tip 8 - PostgreSQL

We connect to PostgreSQL with DBNAME, DBHOST, DBPASS, and DBUSER passed as environment variables and used in [settings.py](./azureproject/settings.py) and [production.py](./azureproject/production.py) to set the [DATABASES variable expected by Django](https://docs.djangoproject.com/en/4.0/ref/settings/#std:setting-DATABASES). This is how we connect, but we must first be able to access the server. That's where networking and firewall rules come into play.

Some ways to deal with networking:

* To allow code in App Service to access PostgreSQL, we set the "Allow public access from any Azure service" networking setting, which works but is a bit loose in terms of security. It allows access to all Azure services.

* Create a firewall rule to explicitly add all the outbound IPs of the Azure App Service. See [Create a firewall rule to explicitly allow outbound IPs](https://docs.microsoft.com/en-us/azure/mysql/howto-connect-webapp#solution-2---create-a-firewall-rule-to-explicitly-allow-outbound-ips). This is not a bad fallback to show or mention.

* The article [Connect with Managed Identity to Azure Database for PostgreSQL](https://docs.microsoft.com/en-us/azure/postgresql/howto-connect-with-managed-identity) looks promising but there isn't a way to get a token from DefaultAzureCredential and pass it to DATABASES Django variable, that we can tell. 

* There is a new way to create a PostgreSQL in it's own VPN and deal with security that way. This isn't generally available at this time.


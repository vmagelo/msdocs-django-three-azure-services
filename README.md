# Deploy a Python (Django) web app with PostgreSQL in Azure

This is a Python (Django) web app using the Django framework with three Azure services: Azure App Service, Azure Database for PostgreSQL relational database service, and Azure Blob Storage. This app is designed to be be run locally and then deployed to Azure. 

| Function      | Local Dev | Azure Hosted |
| ------------- | --------- | ------------ |
| Web app | localhost | App Service |
| Database | Local PostgreSQL instance | Azure PostgreSQL service |
| Storage | Azure Blob Storage or Local emulator like [Azurite emulator for local Azure storage development](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azurite) | Azure Blob Storage |


\*Note that locally, Azure Blob Storage is used as well. 

## Todo

* Add csrf_token, c.f. [here](https://simpleisbetterthancomplex.com/tutorial/2016/08/01/how-to-upload-files-with-django.html)

* Change auth from app service principal to Azure AD account. With a local storage solution, there is no dependency on Azure to run locally,  so no credentials needed. (Though this app would need more coding to catch that we are in dev environment and then use an appropriate local storage.) With no local storage solution (i.e., continue to use Azure Blob Storage), then we should use AD user that has access to storage. How to correctly create AD user?

* When deployed, managed identity would be used. Need to run through this.

![Example review list with images](/static/images/Example-reviews.png)
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

### Tip 4

To work with the Python SDK and Azure Blob Storage, see [Quickstart: Manage blobs with Python v12 SDK](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python).

Create container called *restaurants* and set access level to *Blob (anonymous read access for blobs only)*. It makes this example easier to have images public when **reading**. Could set up the example so that images are accessed through web app and not public, but this would require more coding and would complicate the presentation.

When **writing**, this should be done authenticated. Locally with Azure User or App service principal (registered app) with role. Deployed, with managed identity.

### Tip 5

To work with the HTML input file, make sure the form tag has *encytype*.

```html
<form method="POST" action="{% url 'add_review' restaurant.id %}" enctype="multipart/form-data">
    <label for="reviewImage" class="form-label">Add a photo</label>
    <input type="file" class="form-control" id="reviewImage" name="reviewImage">                    
</form>
```

### Tip 6

This sample app used the Django [messages framework](https://docs.djangoproject.com/en/4.0/ref/contrib/messages/). For example, to pass a message back if there is an error, do this:

```python
messages.add_message(request, messages.INFO, 
    'Restaurant not added. Include at least a restaurant name and description.')
return HttpResponseRedirect(reverse('create_restaurant'))  
```

The message backend is set in [settings.py](./azureproject/settings.py) and [production.py](./azureproject/production.py) with:

```python
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
```

This storage messages in session data.
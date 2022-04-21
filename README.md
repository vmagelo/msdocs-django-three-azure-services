# Deploy a Python (Django) web app with PostgreSQL and Blob Storage in Azure

This is a Python web app using the Django framework with three Azure services: Azure App Service, Azure Database for PostgreSQL relational database service, and Azure Blob Storage. This app is designed to be be run locally and then deployed to Azure. 

| Function      | Local Dev | Azure Hosted |
| ------------- | --------- | ------------ |
| Web app | runs locally, e.g., http://127.0.0.1:8000 | runs in App Service, e.g., https://\<app-name>.azurewebsites.net  |
| Database | Local PostgreSQL instance | Azure PostgreSQL service |
| Storage | Azure Blob Storage* or local emulator like [Azurite emulator for local Azure storage development](https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azurite) | Azure Blob Storage |


\*Current code assumes Azure Blob Storage used locally.

The assumption is that code doesn't change when moving from dev to Azure-hosted. With that in mind, there are two patterns for dealing with authentication:

|   | Local dev | Azure-hosted |
| - | --------- | ------------ |
| pattern&nbsp;1 | app service principal <br> add AZURE_CLIENT_ID, AZURE_TENANT_ID, and AZURE_CLIENT_SECRET to the *.env* file | app service principal <br> configure app settings for AZURE_CLIENT_ID, AZURE_TENANT_ID, and AZURE_CLIENT_SECRET |
| pattern&nbsp;2 | AD group, developer account<br> add AZURE_USERNAME and AZURE_PASSWORD to the *.env* file | managed identity<br> configure as shown in [Authentication Azure-hosted app to Azure resources](https://docs.microsoft.com/en-us/azure/developer/python/sdk/authentication-azure-hosted-apps) |

The code doesn't change between pattern 1 and 2, only what goes into *.env* file.

Example screenshot:

![Example review list with images](/static/images/Example-reviews.png)

## Todo

* Deploy and test managed identity.

* Propagate changes in restaurant review app back to previous Django tutorials, including:
  * csrf token use, don't use exempt in views.py
  * message passing to forms when there is an error (for add review and restaurant), see [views.py](./restaurant_review/views.py) for an example
  * add check of forms looking for blank fields and raise error (for add review and restaurant)
  * check render() lookup on url and make sure they are correct for error conditions, in some cases just use reverse()
  * pull all CSS to [restaurants.css](./static/restaurant.css) and link to from base.html, should be no CSS in other templates
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

When **writing**, this should be done authenticated. Locally with Azure User or App service principal (registered app) with role. Deployed, with managed identity.

### Tip 5

To work with the HTML input file, make sure the form tag has *encytype*.

```html
<form method="POST" action="{% url 'add_review' restaurant.id %}" enctype="multipart/form-data">
    <label for="reviewImage" class="form-label">Add a photo</label>
    <input type="file" class="form-control" id="reviewImage" 
           name="reviewImage" accept="image/png, image/jpeg">                    
</form>
```

The input tag *accept* attribute only filters what can be uploaded in the upload dialog box. It can easily be circumvented by changing the filter. A more rigorous check would be to use a library like [Pillow](https://pillow.readthedocs.io/en/stable/) in Python, or do some other checking in JavaScript before upload. 

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
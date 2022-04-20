import uuid
import os
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Count
from django.urls import reverse
from django.utils import timezone
from django import forms
from PIL import Image

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

from restaurant_review.models import Restaurant, Review

# Create your views here.

def index(request):
    print('Request for index page received')

    restaurants = Restaurant.objects.annotate(avg_rating=Avg('review__rating')).annotate(review_count=Count('review'))
    return render(request, 'restaurant_review/index.html', {'restaurants': restaurants })


def details(request, id):
    print('Request for restaurant details page received')

    try: 
        restaurant = Restaurant.objects.annotate(avg_rating=Avg('review__rating')).annotate(review_count=Count('review')).get(pk=id)
    except Restaurant.DoesNotExist:
        raise Http404("Restaurant doesn't exist")
    return render(request, 'restaurant_review/details.html', {'restaurant': restaurant})


def create_restaurant(request):
    print('Request for add restaurant page received')

    return render(request, 'restaurant_review/create_restaurant.html')


@csrf_exempt
def add_restaurant(request):
    try:
        name = request.POST['restaurant_name']
        street_address = request.POST['street_address']
        description = request.POST['description']
    except (KeyError):
        # Redisplay the question voting form.
        return render(request, 'restaurant_review/add_restaurant.html', {
            'error_message': "You must include a restaurant name, address, and description",
        })
    else:
        restaurant = Restaurant()
        restaurant.name = name
        restaurant.street_address = street_address
        restaurant.description = description
        restaurant.image_name = uuid.uuid4()
        Restaurant.save(restaurant)
                
        return HttpResponseRedirect(reverse('details', args=(restaurant.id,)))

@csrf_exempt
def add_review(request, id):
    try: 
        restaurant = Restaurant.objects.annotate(avg_rating=Avg('review__rating')).annotate(review_count=Count('review')).get(pk=id)
    except Restaurant.DoesNotExist:
        raise Http404("Restaurant doesn't exist")

    try:
        user_name = request.POST['user_name']
        rating = request.POST['rating']
        review_text = request.POST['review_text']
            
    except (KeyError):
        # Redisplay the question voting form.
        return render(request, 'restaurant_review/add_review.html', {
            'error_message': "Error adding review",
        })
    else:

        if 'reviewImage' in request.FILES:
            image_data = request.FILES['reviewImage']
            upload_name = image_data.name
            print("image name = " + upload_name)

            # Create client
            azure_credential = DefaultAzureCredential()
            blob_service_client = BlobServiceClient(
                account_url="https://%s.blob.core.windows.net" % os.environ['STORAGE_ACCOUNT_NAME'],
                credential=azure_credential)

            # Get file
            image_uuid = uuid.uuid4()
            image_name = str(image_uuid) + ".png"
            
            # Create blob client
            blob_client = blob_service_client.get_blob_client(container="restaurants", blob=image_name)
            print("\nUploading to Azure Storage as blob:\n\t" + image_name)

            # Upload file
            with image_data as data:
                blob_client.upload_blob(data)
        else:
            image_name=None

        review = Review()
        review.restaurant = restaurant
        review.review_date = timezone.now()
        review.user_name = user_name
        review.rating = rating
        review.review_text = review_text
        review.image_name = image_name
        Review.save(review)
                
    return HttpResponseRedirect(reverse('details', args=(id,)))        
from django.urls import path
from apps.e_commerce.api.index_api import *
from apps.e_commerce.api.marvel_api_views import *

urlpatterns = [
    path('hello_user/', hello_user),
    path('get_comics/', get_comics),
    path('purchased_item/', purchased_item)
]
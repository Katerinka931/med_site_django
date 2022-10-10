from django.urls import path, re_path
from django.conf.urls import include
from rest_framework.authtoken.views import ObtainAuthToken

urlpatterns = [
    path('', include('MedApp.urls')),
]

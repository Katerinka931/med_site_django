from django.urls import path, re_path
from django.conf.urls import include

from django.contrib import admin

urlpatterns = [
    path('', include('MedApp.urls')),
    re_path(r'^admin/', admin.site.urls),  #http://127.0.0.1:8000/admin
]

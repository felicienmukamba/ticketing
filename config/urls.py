# config/urls.py

from django.contrib import admin
from django.urls import path, include # Assurez-vous que 'include' est importé

urlpatterns = [
    path('admin/', admin.site.urls),
    # Inclure toutes les URLs de l'application ticketing
    path('', include('ticketing.urls')),
]
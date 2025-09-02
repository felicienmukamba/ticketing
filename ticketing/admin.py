# ticketing/admin.py
from django.contrib import admin
from .models import Agent, Spectateur, Programme, Reservation, Paiement

admin.site.register(Agent)
admin.site.register(Spectateur)
admin.site.register(Programme)
admin.site.register(Reservation)
admin.site.register(Paiement)
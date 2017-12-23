from django.contrib import admin
from .models import Document, Contract, Landlord, Renter

# Register your models here.
admin.site.register(Document)
admin.site.register(Contract)
admin.site.register(Landlord)
admin.site.register(Renter)
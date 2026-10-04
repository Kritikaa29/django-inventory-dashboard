from django.contrib import admin
from .models import Supplier, Product

# This tells Django to show these tables in the admin panel
admin.site.register(Supplier)
admin.site.register(Product)
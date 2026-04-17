from django.contrib import admin
from .models import FoodItem, Cart, Order

admin.site.register(FoodItem)
admin.site.register(Cart)
admin.site.register(Order)

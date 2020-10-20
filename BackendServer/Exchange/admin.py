from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Profile)
admin.site.register(Stock)
admin.site.register(Company)
admin.site.register(UserStock)
admin.site.register(BuyOffer)
admin.site.register(SellOffer)
admin.site.register(Transaction)
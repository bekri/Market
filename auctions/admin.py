# admin.py

from django.contrib import admin
from .models import Listings, Bids, Comments, Category, Watchlist, User

# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Listings)
admin.site.register(Bids)
admin.site.register(Comments)
admin.site.register(Watchlist)
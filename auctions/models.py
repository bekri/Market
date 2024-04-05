from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Listings(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='auctions/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Modify to use ForeignKey
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='listings')
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Bids(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='bids')
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, null=True, related_name='bids')
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class Comments(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='comments')
    comment = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE, null=True, related_name='comments')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    listings = models.ManyToManyField('Listings', null=True, related_name='watchlist')

    def __str__(self):
        return f"{self.user}'s Watchlist"

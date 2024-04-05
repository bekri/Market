from django import forms
from .models import Listings, Bids, Comments 

from django import forms
from .models import Listings

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listings
        fields = ['title', 'description', 'starting_bid', 'image', 'category']

class BidForm(forms.ModelForm):
    class Meta:
        model = Bids
        fields = ['bid_amount']
        
class CommentForm(forms.ModelForm):
    class Meta: 
        model = Comments
        fields = ['comment']


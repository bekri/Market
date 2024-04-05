from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import ListingForm, BidForm, CommentForm
from .models import Listings, Bids, Watchlist, Comments, User, Category
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.http import JsonResponse

from .models import User


def index(request):
    return render(request, "auctions/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    


def listings_view(request):
    active_listings = Listings.objects.filter(active=True)
    return render(request, 'listings.html', {'active_listings': active_listings})

# Add user association:
# create a new item
@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.save()
            return redirect('listing_detail', listing.id)
    else:
        form = ListingForm()
    
    # Get all available categories
    categories = Category.objects.all()
    
    return render(request, 'auctions/create_listing.html', {'form': form, 'categories': categories})


# active  listings

# details of item
from .forms import CommentForm

from django.contrib import messages

def listing_detail(request, listing_id):
    listing = get_object_or_404(Listings, pk=listing_id)
    category = listing.category
    is_seller = request.user == listing.seller
    highest_bid = Bids.objects.filter(listing=listing).order_by('-bid_amount').first()

    if request.user.is_authenticated:
        user_watchlist = Watchlist.objects.filter(user=request.user, listings=listing).exists()
        initial_data = {'commenter': request.user.username}  # Set the commenter field value to the logged-in user's username
    else:
        user_watchlist = False
        initial_data = {}

    winner = None
    if not listing.active and highest_bid:
        winner = highest_bid.bidder

    comments = Comments.objects.filter(listing=listing)  # Get all comments for the listing
    comment_data = []  # List to store comment data including commenter's username
    for comment in comments:
        comment_data.append({'comment': comment, 'commenter_username': comment.commenter.username})

    context = {
        'listing': listing,
        'listing_id': listing_id,
        'highest_bid': highest_bid,
        'listing_in_watchlist': user_watchlist,
        'is_seller': is_seller,
        'winner': winner,
        'category': category,
        'form': CommentForm(initial=initial_data),
        'comments': comment_data,  # Pass comments and commenter usernames to the template
    }
    
    # Handle comment submission
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.listing = listing
            comment.save()
            messages.success(request, "Your comment has been added.")
            return redirect('listing_detail', listing_id=listing_id)
        else:
            messages.error(request, "Invalid comment form.")
    
    return render(request, 'auctions/listing_detail.html', context)

# Items  on the hoe page "lists"
def listings(request):
    listings = Listings.objects.all()
    
    # Get categories for each listing
    categories = {listing.id: listing.category for listing in listings}
    
    return render(request, 'auctions/index.html', {'listings': listings, 'categories': categories})
    


# create Bids
@login_required
def create_bid(request, listing_id):
    listing = get_object_or_404(Listings, pk=listing_id)
    
    if request.method == 'POST':
        if listing.active:  # Check if the listing is active (bidding is open)
            form = BidForm(request.POST)
            if form.is_valid():
                bid_amount = form.cleaned_data['bid_amount']
                
                # Get the highest bid for the listing
                highest_bid = Bids.objects.filter(listing=listing).aggregate(Max('bid_amount'))['bid_amount__max']
                if highest_bid is None:
                    highest_bid = listing.starting_bid
                
                if bid_amount > highest_bid:
                    bid = form.save(commit=False)
                    bid.bidder = request.user
                    bid.listing = listing
                    bid.save()
                    
                    # Update the current bid on the listing (optional)
                    # listing.current_bid = bid_amount
                    # listing.save()
                    
                    messages.success(request, 'Your bid has been placed successfully.')
                    return redirect('listing_detail', listing_id)
                else:
                    messages.error(request, 'Your bid amount must be higher than the current highest bid.')
            else:
                messages.error(request, 'Invalid bid form.')
        else:
            messages.error(request, 'Bidding for this listing is closed.')
    
    return redirect('listing_detail', listing_id)



# watchlist
@login_required
def manage_watchlist(request, listing_id):
    if request.method == 'POST':
        listing = get_object_or_404(Listings, pk=listing_id)
        user_watchlist, created = Watchlist.objects.get_or_create(user=request.user)
        if listing in user_watchlist.listings.all():
            user_watchlist.listings.remove(listing)
            added_to_watchlist = False
        else:
            user_watchlist.listings.add(listing)
            added_to_watchlist = True
        return JsonResponse({'added_to_watchlist': added_to_watchlist})

#manage watchlist without id : couldn't find a way to make the code do both at same time, sorry poor code !
@login_required
def manage_watchlist(request, listing_id=None):  # Make listing_id optional with a default value of None
    if listing_id is not None:  # Check if a listing_id is provided
        # Get the listing object
        listing = Listings.objects.get(pk=listing_id)
        user = request.user

        # Get or create the user's watchlist
        user_watchlist, created = Watchlist.objects.get_or_create(user=user)
    
        # Check if the listing is already in the user's watchlist
        if user_watchlist.listings.filter(pk=listing_id).exists():
            # Remove the listing from the user's watchlist
            user_watchlist.listings.remove(listing)
            added_to_watchlist = False
        else:
            # Add the listing to the user's watchlist
            user_watchlist.listings.add(listing)
            added_to_watchlist = True

        # Fetch the user's watchlist again
        watchlist_listings = user_watchlist.listings.all()

        # Render the template with the watchlist listings and the updated status
        return render(request, 'auctions/manage_watchlist.html', {'watchlist_listings': watchlist_listings, 'added_to_watchlist': added_to_watchlist})

    else:  # If no listing_id is provided, simply display the user's watchlist
        user_watchlist, created = Watchlist.objects.get_or_create(user=request.user)
        watchlist_listings = user_watchlist.listings.all()
        return render(request, 'auctions/manage_watchlist.html', {'watchlist_listings': watchlist_listings})






# Comment
@login_required
def add_comment(request, listing_id):
    listing = get_object_or_404(Listings, id=listing_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.commenter = request.user
            comment.listing = listing
            comment.save()
            return redirect('listing_detail', listing_id=listing_id)
    else:
        form = CommentForm()

    return render(request, 'listing_detail.html', {'form': form})

# Home page index show  listings
def index(request):
    # Query only active listings
    all_listings = Listings.objects.filter(active=True)
    categories = Category.objects.all()  # Query all categories from the database
    return render(request, "auctions/index.html", {'all_listings': all_listings, 'categories': categories})



# Close auction if seller
@login_required
def close_auction(request, listing_id):
    listing = get_object_or_404(Listings, pk=listing_id)
    
    # Check if the logged-in user is the seller and if the auction is active
    if request.user == listing.seller and listing.active:
        # Get the highest bid for the listing
        highest_bid = Bids.objects.filter(listing=listing).order_by('-bid_amount').first()
        if highest_bid:
            # Mark the highest bidder as the winner
            listing.winner = highest_bid.bidder
            listing.active = False
            listing.save()
            # Additional logic (e.g., notifying the winner) can be added here
            return HttpResponseRedirect(reverse('listing_detail', args=[listing_id]))
    
    # Redirect to the listing detail page if the user is not the seller or if there are no bids or if the auction is already closed
    return HttpResponseRedirect(reverse('listing_detail', args=[listing_id]))


def category_listings(request, category_id):
    category = Category.objects.get(pk=category_id)
    listings = Listings.objects.filter(category=category, active=True)
    return render(request, 'auctions/category_listings.html', {'listings': listings, 'category': category})
# Example view function
def some_view(request):
    categories = Category.objects.all()  # Fetch all categories from the database
    return render(request, 'auctions/layout.html', {'categories': categories})
def categories_view(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {'categories': categories})


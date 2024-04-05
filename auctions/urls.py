from django.urls import path
from .views import listings_view
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("manage_watchlist", views.manage_watchlist, name="manage_watchlist"),

     # Listings
    path('listings/', listings_view, name='listings'),
    path("listings/<int:listing_id>/", views.listing_detail, name="listing_detail"),
    path("create_listing/", views.create_listing, name="create_listing"),

    # Bids
    path("bids/<int:listing_id>/", views.create_bid, name="create_bid"),

    # Comments
    path("comments/<int:listing_id>/", views.add_comment, name="add_comment"),

    # Watchlist
    path('manage_watchlist/', views.manage_watchlist, name='manage_watchlist'),  # No listing_id required
    path('manage_watchlist/<int:listing_id>/', views.manage_watchlist, name='manage_watchlist'),
    # close auction
    path("close_auction/<int:listing_id>/", views.close_auction, name="close_auction"),


    # Category
    # Add the new URL pattern for displaying listings by category
    path("category/<int:category_id>/", views.category_listings, name="category_listings"),
    path("categories/", views.categories_view, name="categories"),
    

]

from django.urls import path
from . import views
from . import admin_views

app_name = 'core'

urlpatterns = [
    # Main Pages
    path('', views.home, name='home'),
    path('search/', views.search_listings, name='search'),
    path('listing/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('sell/', views.create_listing, name='create_listing'),
    path('dashboard/', views.seller_dashboard, name='dashboard'),
    path('compare/', views.compare_listings, name='compare'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Admin Dashboard (Superuser only)
    path('admin-dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/approve/<int:pk>/', admin_views.approve_listing, name='approve_listing'),
    path('admin-dashboard/reject/<int:pk>/', admin_views.reject_listing, name='reject_listing'),
    
    # AJAX Endpoints for Cascading Dropdowns
    path('ajax/load-models/', views.load_models, name='ajax_load_models'),
    path('ajax/load-trims/', views.load_trims, name='ajax_load_trims'),
    path('ajax/reveal-phone/<int:pk>/', views.reveal_phone, name='reveal_phone'),
]

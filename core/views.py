from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout, login, authenticate
from django.http import JsonResponse
from django.db.models import Q, F
from django.utils import timezone
from django.utils.translation import gettext as _
from django.contrib import messages
from .models import Listing, Make, Model, CarTrim
from .forms import ListingForm, UserRegistrationForm, UserUpdateForm

def home(request):
    """Homepage with featured listings"""
    featured_listings = Listing.objects.filter(status='ACTIVE').order_by('-created_at')[:8]
    makes = Make.objects.all()
    
    context = {
        'featured_listings': featured_listings,
        'makes': makes,
        'governorates': Listing.GOVERNORATES,
    }
    return render(request, 'home.html', context)

def search_listings(request):
    """Advanced search and filter listings"""
    listings = Listing.objects.filter(status='ACTIVE').select_related('trim__model__make', 'seller')
    
    # Keyword search
    query = request.GET.get('q')
    if query:
        listings = listings.filter(
            Q(trim__model__name_en__icontains=query) |
            Q(trim__model__name_ar__icontains=query) |
            Q(trim__model__make__name_en__icontains=query) |
            Q(trim__model__make__name_ar__icontains=query) |
            Q(description__icontains=query)
        )
    
    # Filter by make
    make_id = request.GET.get('make')
    if make_id:
        listings = listings.filter(trim__model__make_id=make_id)
    
    # Filter by model
    model_id = request.GET.get('model')
    if model_id:
        listings = listings.filter(trim__model_id=model_id)
    
    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        listings = listings.filter(price__gte=min_price)
    if max_price:
        listings = listings.filter(price__lte=max_price)
    
    # Filter by year range
    min_year = request.GET.get('min_year')
    max_year = request.GET.get('max_year')
    if min_year:
        listings = listings.filter(trim__year__gte=min_year)
    if max_year:
        listings = listings.filter(trim__year__lte=max_year)
    
    # Filter by governorate
    governorate = request.GET.get('governorate')
    if governorate:
        listings = listings.filter(location=governorate)
    
    # Filter by transmission
    transmission = request.GET.get('transmission')
    if transmission:
        listings = listings.filter(trim__transmission=transmission)
    
    # Filter by fuel type
    fuel_type = request.GET.get('fuel_type')
    if fuel_type:
        listings = listings.filter(trim__fuel_type=fuel_type)
    
    # Filter by mileage
    max_mileage = request.GET.get('max_mileage')
    if max_mileage:
        listings = listings.filter(mileage__lte=max_mileage)
    
    # Filter by color
    color = request.GET.get('color')
    if color:
        listings = listings.filter(color__iexact=color)
    
    # Filter by seller type
    seller_type = request.GET.get('seller_type')
    if seller_type == 'dealer':
        listings = listings.filter(seller__is_dealer=True)
    elif seller_type == 'private':
        listings = listings.filter(seller__is_dealer=False)
    
    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        listings = listings.order_by('price')
    elif sort_by == 'price_high':
        listings = listings.order_by('-price')
    elif sort_by == 'mileage_low':
        listings = listings.order_by('mileage')
    elif sort_by == 'year_new':
        listings = listings.order_by('-trim__year')
    elif sort_by == 'views':
        listings = listings.order_by('-views')
    else:  # newest (default)
        listings = listings.order_by('-created_at')
    
    # Get all makes and models for dropdowns
    makes = Make.objects.all()
    models = Model.objects.filter(make_id=make_id) if make_id else Model.objects.none()
    
    context = {
        'listings': listings,
        'makes': makes,
        'models': models,
        'total_count': listings.count(),
        'governorates': Listing.GOVERNORATES,
        # Pass back filter values for selected states
        'filters': {
            'q': query or '',
            'make': make_id or '',
            'model': model_id or '',
            'min_price': min_price or '',
            'max_price': max_price or '',
            'min_year': min_year or '',
            'max_year': max_year or '',
            'governorate': governorate or '',
            'transmission': transmission or '',
            'fuel_type': fuel_type or '',
            'max_mileage': max_mileage or '',
            'color': color or '',
            'seller_type': seller_type or '',
            'sort': sort_by,
        },
    }
    return render(request, 'search.html', context)

def listing_detail(request, pk):
    """Individual listing detail page"""
    # Use select_related to optimize DB queries
    listing = get_object_or_404(Listing.objects.select_related('trim__model__make', 'seller'), pk=pk, status='ACTIVE')
    
    # Increment view count atomically
    Listing.objects.filter(pk=pk).update(views=F('views') + 1)
    # Refresh to get updated value if needed, though for display we might just use the old one + 1 logic or re-fetch if critical. 
    # For now, just display the object as retrieved (it will show N, logic updates to N+1 in DB)
    
    # Get related listings (same make)
    related_listings = Listing.objects.filter(
        trim__model__make=listing.trim.model.make,
        status='ACTIVE'
    ).exclude(pk=pk).select_related('trim__model__make')[:4]
    
    context = {
        'listing': listing,
        'related_listings': related_listings,
    }
    return render(request, 'listing_detail.html', context)

@login_required
def create_listing(request):
    """Create a new listing"""
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.status = 'PENDING'  # Requires admin approval
            listing.save()
            return redirect('core:dashboard')
    else:
        form = ListingForm()
    
    context = {
        'form': form,
        'makes': Make.objects.all(),
    }
    return render(request, 'listing_form.html', context)

@login_required
def seller_dashboard(request):
    """Seller dashboard with their listings"""
    listings = Listing.objects.filter(seller=request.user).order_by('-created_at')
    
    # Statistics
    stats = {
        'total': listings.count(),
        'active': listings.filter(status='ACTIVE').count(),
        'pending': listings.filter(status='PENDING').count(),
        'sold': listings.filter(status='SOLD').count(),
        'total_views': sum(listing.views for listing in listings),
        'total_phone_clicks': sum(listing.phone_clicks for listing in listings),
    }
    
    context = {
        'listings': listings,
        'stats': stats,
    }
    return render(request, 'dashboard.html', context)

# --- AJAX Endpoints ---
def load_models(request):
    """AJAX endpoint to load models based on selected make"""
    make_id = request.GET.get('make_id')
    models = Model.objects.filter(make_id=make_id).order_by('name_en')
    
    # Return JSON with localized names
    lang = request.LANGUAGE_CODE
    data = []
    for model in models:
        data.append({
            'id': model.id,
            'name': model.name_ar if lang == 'ar' else model.name_en
        })
    
    return JsonResponse(data, safe=False)

def load_trims(request):
    """AJAX endpoint to load trims based on selected model"""
    model_id = request.GET.get('model_id')
    trims = CarTrim.objects.filter(model_id=model_id).order_by('-year', 'name')
    
    data = []
    for trim in trims:
        # Display format: "2024 - 1.6L Highline Auto"
        display_name = f"{trim.year} - {trim.name} ({trim.get_transmission_display()})"
        data.append({
            'id': trim.id,
            'name': trim.name,
            'year': trim.year,
            'display': display_name,
            'horsepower': trim.horsepower,
            'fuel_consumption': trim.fuel_consumption,
        })
    
    return JsonResponse(data, safe=False)

def reveal_phone(request, pk):
    """AJAX endpoint to reveal phone number and track clicks"""
    listing = get_object_or_404(Listing, pk=pk, status='ACTIVE')
    
    # Increment phone click counter atomically
    Listing.objects.filter(pk=pk).update(phone_clicks=F('phone_clicks') + 1)
    
    return JsonResponse({
        'phone_number': listing.seller.phone_number
    })

def login_view(request):
    """Email-based login view""" 
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Try to find user by email
        from .models import User
        try:
            user_obj = User.objects.get(email=email)
            # Authenticate with username
            user = authenticate(request, username=user_obj.username, password=password)
            
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'core:home')
                return redirect(next_url)
            else:
                context = {'error': _('Invalid email or password')}
                return render(request, 'login.html', context)
        except User.DoesNotExist:
            context = {'error': _('No account found with this email')}
            return render(request, 'login.html', context)
    
    return render(request, 'login.html')

def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('core:home')
    else:
        form = UserRegistrationForm()

    context = {'form': form}
    return render(request, 'register.html', context)

@login_required
def logout_view(request):
    """Logout user"""
    auth_logout(request)
    return redirect('core:home')

@login_required
def edit_profile(request):
    """Update user profile"""
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your profile has been updated successfully.'))
            return redirect('core:edit_profile')
    else:
        form = UserUpdateForm(instance=request.user)

    context = {
        'form': form
    }
    return render(request, 'edit_profile.html', context)

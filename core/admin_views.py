"""
Admin views for listing approval dashboard.
Superuser-only views for managing pending listings.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext as _
from django.db.models import Count
from .models import Listing


def superuser_required(view_func):
    """Decorator to require superuser access"""
    decorated_view_func = login_required(user_passes_test(lambda u: u.is_superuser)(view_func))
    return decorated_view_func


@superuser_required
def admin_dashboard(request):
    """Admin dashboard showing pending listings and stats"""
    pending_listings = Listing.objects.filter(status='PENDING').select_related(
        'trim__model__make', 'seller'
    ).order_by('-created_at')
    
    stats = {
        'pending': pending_listings.count(),
        'active': Listing.objects.filter(status='ACTIVE').count(),
        'sold': Listing.objects.filter(status='SOLD').count(),
        'total': Listing.objects.count(),
    }
    
    context = {
        'pending_listings': pending_listings,
        'stats': stats,
    }
    return render(request, 'admin_dashboard.html', context)


@superuser_required
def approve_listing(request, pk):
    """Approve a pending listing"""
    listing = get_object_or_404(Listing, pk=pk, status='PENDING')
    listing.status = 'ACTIVE'
    listing.save(update_fields=['status'])
    messages.success(request, _('Listing approved successfully.'))
    return redirect('core:admin_dashboard')


@superuser_required
def reject_listing(request, pk):
    """Reject a pending listing"""
    listing = get_object_or_404(Listing, pk=pk, status='PENDING')
    listing.status = 'REJECTED'
    listing.save(update_fields=['status'])
    messages.warning(request, _('Listing rejected.'))
    return redirect('core:admin_dashboard')

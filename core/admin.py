from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Make, Model, CarTrim, Listing

# --- User Admin ---
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('Dealer Information'), {
            'fields': ('is_dealer', 'phone_number', 'is_verified_dealer', 'commercial_registry', 'tax_card')
        }),
    )
    list_display = ['username', 'email', 'phone_number', 'is_dealer', 'is_verified_dealer', 'is_staff']
    list_filter = ['is_dealer', 'is_verified_dealer', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'phone_number']

# --- Master Data Admin ---
@admin.register(Make)
class MakeAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ar']
    search_fields = ['name_en', 'name_ar']

@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_ar', 'make', 'category']
    list_filter = ['make', 'category']
    search_fields = ['name_en', 'name_ar']

@admin.register(CarTrim)
class CarTrimAdmin(admin.ModelAdmin):
    list_display = ['model', 'name', 'year', 'transmission', 'fuel_type', 'horsepower']
    list_filter = ['year', 'transmission', 'fuel_type', 'model__make']
    search_fields = ['name', 'model__name_en', 'model__name_ar']
    ordering = ['-year', 'model']

# --- Listings Admin ---
from modeltranslation.admin import TranslationAdmin

@admin.register(Listing)
class ListingAdmin(TranslationAdmin):
    list_display = ['trim', 'seller', 'price', 'location', 'status', 'views', 'created_at']
    list_filter = ['status', 'location', 'created_at', 'trim__model__make']
    search_fields = ['trim__model__name_en', 'seller__username', 'description']
    readonly_fields = ['views', 'phone_clicks', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Car Information'), {
            'fields': ('trim', 'price', 'odometer', 'color', 'location')
        }),
        (_('Description'), {
            'fields': ('description',)
        }),
        (_('Images'), {
            'fields': ('image_main', 'image_2', 'image_3', 'image_4', 'image_5')
        }),
        (_('Seller & Status'), {
            'fields': ('seller', 'status', 'active_date')
        }),
        (_('Statistics'), {
            'fields': ('views', 'phone_clicks', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-set seller to current user if creating new listing"""
        if not change and not obj.seller_id:
            obj.seller = request.user
        super().save_model(request, obj, form, change)

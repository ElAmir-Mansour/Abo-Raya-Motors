from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _

# --- Utilities ---
def compress_image(image_field, filename):
    """
    Compress and convert images to WebP format with max width of 1200px
    """
    im = Image.open(image_field)
    if im.mode in ("RGBA", "P"): 
        im = im.convert("RGB")
    if im.width > 1200:
        output_size = (1200, int(im.height * (1200/im.width)))
        im.thumbnail(output_size)
    im_io = BytesIO()
    im.save(im_io, format='WEBP', quality=75)
    new_filename = f"{filename.split('.')[0]}.webp"
    return ContentFile(im_io.getvalue()), new_filename

# --- 1. Authentication ---
class User(AbstractUser):
    """Extended user model with dealer capabilities"""
    is_dealer = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    # Egypt Compliance Documents
    commercial_registry = models.ImageField(upload_to='private/docs/', blank=True)
    tax_card = models.ImageField(upload_to='private/docs/', blank=True)
    is_verified_dealer = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

# --- 2. Master Data (Auto-Fill Engine) ---
class Make(models.Model):
    """Car manufacturer/brand"""
    name_en = models.CharField(max_length=50, verbose_name=_("Name (English)"))
    name_ar = models.CharField(max_length=50, verbose_name=_("Name (Arabic)"))
    logo = models.ImageField(upload_to='logos/')

    def __str__(self): 
        return self.name_en

    class Meta:
        verbose_name = _("Make")
        verbose_name_plural = _("Makes")
        ordering = ['name_en']

class Model(models.Model):
    """Car model linked to a manufacturer"""
    make = models.ForeignKey(Make, on_delete=models.CASCADE, related_name='models')
    name_en = models.CharField(max_length=50, verbose_name=_("Name (English)"))
    name_ar = models.CharField(max_length=50, verbose_name=_("Name (Arabic)"))
    category = models.CharField(max_length=20, help_text="e.g., Sedan, SUV, Coupe")

    def __str__(self): 
        return f"{self.make.name_en} {self.name_en}"

    class Meta:
        verbose_name = _("Model")
        verbose_name_plural = _("Models")
        ordering = ['make', 'name_en']

class CarTrim(models.Model):
    """Detailed car specifications to prevent user input errors"""
    TRANSMISSION_CHOICES = [
        ('AUTO', _('Automatic')), 
        ('MANUAL', _('Manual'))
    ]
    FUEL_CHOICES = [
        ('PETROL', _('Petrol')), 
        ('DIESEL', _('Diesel')),
        ('ELECTRIC', _('Electric')),
        ('HYBRID', _('Hybrid'))
    ]

    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name='trims')
    name = models.CharField(max_length=100, help_text="e.g., '1.6L Highline'")
    year = models.IntegerField()
    engine_cc = models.IntegerField(verbose_name=_("Engine CC"))
    horsepower = models.IntegerField(verbose_name=_("Horsepower"))
    fuel_consumption = models.FloatField(help_text=_("Liters/100km"))
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)

    def __str__(self): 
        return f"{self.model.name_en} {self.name} ({self.year})"

    class Meta:
        verbose_name = _("Car Trim")
        verbose_name_plural = _("Car Trims")
        ordering = ['-year', 'model']

# --- 3. Listings ---
class Listing(models.Model):
    """Main car listing model"""
    STATUS_CHOICES = [
        ('DRAFT', _('Draft')), 
        ('PENDING', _('Pending')), 
        ('ACTIVE', _('Active')), 
        ('SOLD', _('Sold')), 
        ('EXPIRED', _('Expired'))
    ]
    GOVERNORATES = [
        ('CAIRO', _('Cairo')), 
        ('ALEX', _('Alexandria')), 
        ('GIZA', _('Giza')),
        ('SHARM', _('Sharm El Sheikh')),
        ('HURGHADA', _('Hurghada')),
        ('ALAMEIN', _('El Alamein')),
        ('DAHAB', _('Dahab')),
        ('MARSA_ALAM', _('Marsa Alam')),
        ('SIWA', _('Siwa Oasis')),
        ('QALIUBIYA', _('Qaliubiya')),
        ('SHARKIA', _('Sharkia')),
        ('DAKAHLIA', _('Dakahlia')),
        ('GHARBIA', _('Gharbia')),
        ('MENOUFIA', _('Menoufia')),
        ('BEHEIRA', _('Beheira')),
        ('KAFR_EL_SHEIKH', _('Kafr El Sheikh')),
        ('DAMIETTA', _('Damietta')),
        ('PORT_SAID', _('Port Said')),
        ('ISMAILIA', _('Ismailia')),
        ('SUEZ', _('Suez')),
        ('NORTH_SINAI', _('North Sinai')),
        ('SOUTH_SINAI', _('South Sinai')),
        ('RED_SEA', _('Red Sea')),
        ('FAIYUM', _('Faiyum')),
        ('BENI_SUEF', _('Beni Suef')),
        ('MINYA', _('Minya')),
        ('ASYUT', _('Asyut')),
        ('SOHAG', _('Sohag')),
        ('QENA', _('Qena')),
        ('LUXOR', _('Luxor')),
        ('ASWAN', _('Aswan')),
        ('NEW_VALLEY', _('New Valley')),
        ('MATROUH', _('Matrouh'))
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    trim = models.ForeignKey(CarTrim, on_delete=models.PROTECT, verbose_name=_("Car Trim"))
    
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Price (EGP)"))
    odometer = models.IntegerField(verbose_name=_("Odometer (km)"))
    color = models.CharField(max_length=30, verbose_name=_("Color"))
    description = models.TextField(verbose_name=_("Description"))
    location = models.CharField(max_length=20, choices=GOVERNORATES, verbose_name=_("Location"))
    
    # Media - up to 5 images
    image_main = models.ImageField(upload_to='cars/%Y/%m/', verbose_name=_("Main Image"))
    image_2 = models.ImageField(upload_to='cars/%Y/%m/', blank=True, verbose_name=_("Image 2"))
    image_3 = models.ImageField(upload_to='cars/%Y/%m/', blank=True, verbose_name=_("Image 3"))
    image_4 = models.ImageField(upload_to='cars/%Y/%m/', blank=True, verbose_name=_("Image 4"))
    image_5 = models.ImageField(upload_to='cars/%Y/%m/', blank=True, verbose_name=_("Image 5"))
    
    status = models.CharField(choices=STATUS_CHOICES, default='PENDING', max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active_date = models.DateTimeField(null=True, blank=True, help_text=_("Set when admin approves"))
    views = models.IntegerField(default=0, verbose_name=_("View Count"))
    phone_clicks = models.IntegerField(default=0, verbose_name=_("Phone Reveal Clicks"))

    @property
    def mileage(self):
        """Alias for odometer field for template compatibility"""
        return self.odometer

    @property
    def price_int(self):
        """Return price as integer for display without decimals"""
        return int(self.price) if self.price else 0

    def save(self, *args, **kwargs):
        """Auto-compress images on save"""
        # Compress all uploaded images
        for field_name in ['image_main', 'image_2', 'image_3', 'image_4', 'image_5']:
            image_field = getattr(self, field_name)
            if image_field and hasattr(image_field, 'file') and not image_field.name.endswith('.webp'):
                try:
                    compressed_file, new_name = compress_image(image_field, image_field.name)
                    image_field.save(new_name, compressed_file, save=False)
                except Exception as e:
                    # Log error but don't fail the save
                    print(f"Error compressing {field_name}: {e}")
        
        super().save(*args, **kwargs)

    def __str__(self): 
        return f"{self.trim} - {self.price} EGP ({self.status})"

    class Meta:
        verbose_name = _("Listing")
        verbose_name_plural = _("Listings")
        ordering = ['-created_at']


# --- 4. Favorites ---
class Favorite(models.Model):
    """User's saved/favorited car listings"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → {self.listing}"

    class Meta:
        verbose_name = _("Favorite")
        verbose_name_plural = _("Favorites")
        unique_together = ['user', 'listing']
        ordering = ['-created_at']

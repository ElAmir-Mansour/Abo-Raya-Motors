"""
Management command to populate the database with sample data
Usage: python manage.py populate_sample_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Make, Model, CarTrim, Listing
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with sample car data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Create test users
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@aboraaya.com',
                password='admin123',
                phone_number='+201234567890'
            )
            self.stdout.write(self.style.SUCCESS('✓ Created superuser (admin/admin123)'))
        else:
            admin = User.objects.get(username='admin')
        
        if not User.objects.filter(username='dealer1').exists():
            dealer = User.objects.create_user(
                username='dealer1',
                email='dealer@aboraaya.com',
                password='dealer123',
                phone_number='+201234567891',
                is_dealer=True,
                is_verified_dealer=True
            )
            self.stdout.write(self.style.SUCCESS('✓ Created dealer user (dealer1/dealer123)'))
        else:
            dealer = User.objects.get(username='dealer1')
        
        # Create Makes
        makes_data = [
            {'name_en': 'Toyota', 'name_ar': 'تويوتا'},
            {'name_en': 'BMW', 'name_ar': 'بي إم دبليو'},
            {'name_en': 'Mercedes-Benz', 'name_ar': 'مرسيدس بنز'},
            {'name_en': 'Hyundai', 'name_ar': 'هيونداي'},
        ]
        
        makes = {}
        for make_data in makes_data:
            make, created = Make.objects.get_or_create(
                name_en=make_data['name_en'],
                defaults=make_data
            )
            makes[make_data['name_en']] = make
            if created:
                self.stdout.write(f'✓ Created make: {make_data["name_en"]}')
        
        # Create Models
        models_data = [
            {'make': 'Toyota', 'name_en': 'Camry', 'name_ar': 'كامري', 'category': 'Sedan'},
            {'make': 'Toyota', 'name_en': 'RAV4', 'name_ar': 'راف فور', 'category': 'SUV'},
            {'make': 'BMW', 'name_en': '320i', 'name_ar': '320i', 'category': 'Sedan'},
            {'make': 'BMW', 'name_en': 'X5', 'name_ar': 'X5', 'category': 'SUV'},
            {'make': 'Mercedes-Benz', 'name_en': 'C-Class', 'name_ar': 'الفئة C', 'category': 'Sedan'},
            {'make': 'Hyundai', 'name_en': 'Elantra', 'name_ar': 'النترا', 'category': 'Sedan'},
        ]
        
        models = {}
        for model_data in models_data:
            make_name = model_data.pop('make')
            model, created = Model.objects.get_or_create(
                make=makes[make_name],
                name_en=model_data['name_en'],
                defaults=model_data
            )
            models[f"{make_name}_{model_data['name_en']}"] = model
            if created:
                self.stdout.write(f'✓ Created model: {make_name} {model_data["name_en"]}')
        
        # Create CarTrims
        trims_data = [
            {
                'model': 'Toyota_Camry',
                'name': '2.5L Grande',
                'year': 2024,
                'engine_cc': 2500,
                'horsepower': 203,
                'fuel_consumption': 6.3,
                'transmission': 'AUTO',
                'fuel_type': 'PETROL'
            },
            {
                'model': 'Toyota_RAV4',
                'name': '2.5L Hybrid',
                'year': 2023,
                'engine_cc': 2500,
                'horsepower': 219,
                'fuel_consumption': 5.8,
                'transmission': 'AUTO',
                'fuel_type': 'HYBRID'
            },
            {
                'model': 'BMW_320i',
                'name': '2.0L M Sport',
                'year': 2024,
                'engine_cc': 2000,
                'horsepower': 184,
                'fuel_consumption': 6.4,
                'transmission': 'AUTO',
                'fuel_type': 'PETROL'
            },
            {
                'model': 'BMW_X5',
                'name': '3.0L xDrive',
                'year': 2023,
                'engine_cc': 3000,
                'horsepower': 335,
                'fuel_consumption': 9.1,
                'transmission': 'AUTO',
                'fuel_type': 'PETROL'
            },
            {
                'model': 'Mercedes-Benz_C-Class',
                'name': 'C200 AMG',
                'year': 2024,
                'engine_cc': 2000,
                'horsepower': 204,
                'fuel_consumption': 6.7,
                'transmission': 'AUTO',
                'fuel_type': 'PETROL'
            },
            {
                'model': 'Hyundai_Elantra',
                'name': '1.6L Smart',
                'year': 2023,
                'engine_cc': 1600,
                'horsepower': 123,
                'fuel_consumption': 5.5,
                'transmission': 'AUTO',
                'fuel_type': 'PETROL'
            },
        ]
        
        trims = []
        for trim_data in trims_data:
            model_key = trim_data.pop('model')
            trim, created = CarTrim.objects.get_or_create(
                model=models[model_key],
                name=trim_data['name'],
                year=trim_data['year'],
                defaults=trim_data
            )
            trims.append(trim)
            if created:
                self.stdout.write(f'✓ Created trim: {trim}')
        
        # Create Sample Listings
        listings_data = [
            {
                'trim': trims[0],  # Toyota Camry
                'price': Decimal('350000'),
                'odometer': 15000,
                'color': 'White',
                'color': 'White',
                'description_en': 'Brand new condition, single owner, full service history. Excellent fuel economy and very comfortable.',
                'description_ar': 'حالة ممتازة كالجديد، أول مالك، صيانة بالتوكيل. استهلاك وقود ممتاز ومريحة جداً.',
                'location': 'CAIRO',
                'seller': dealer,
                'status': 'ACTIVE'
            },
            {
                'trim': trims[1],  # Toyota RAV4
                'price': Decimal('520000'),
                'odometer': 25000,
                'color': 'Silver',
                'color': 'Silver',
                'description_en': 'Hybrid model, excellent fuel economy, well maintained, garage kept.',
                'description_ar': 'موديل هايبرد، استهلاك وقود ممتاز، صيانة منتظمة، محفوظة بالجراج.',
                'location': 'ALEX',
                'seller': dealer,
                'status': 'ACTIVE'
            },
            {
                'trim': trims[2],  # BMW 320i
                'price': Decimal('680000'),
                'odometer': 8000,
                'color': 'Black',
                'color': 'Black',
                'description_en': 'M Sport package, premium interior, low mileage, immaculate condition.',
                'description_ar': 'باقة إم سبورت، فرش جلد فاخر، ممشى قليل، حالة نادرة.',
                'location': 'CAIRO',
                'seller': admin,
                'status': 'ACTIVE'
            },
            {
                'trim': trims[3],  # BMW X5
                'price': Decimal('1250000'),
                'odometer': 35000,
                'color': 'Blue',
                'color': 'Blue',
                'description_en': 'Powerful 6-cylinder, luxury SUV, fully loaded, excellent performance.',
                'description_ar': 'محرك 6 سلندر قوي، سيارة دفع رباعي فاخرة، كاملة الكماليات، أداء ممتاز.',
                'location': 'GIZA',
                'seller': admin,
                'status': 'ACTIVE'
            },
            {
                'trim': trims[4],  # Mercedes C-Class
                'price': Decimal('750000'),
                'odometer': 12000,
                'color': 'Red',
                'color': 'Red',
                'description_en': 'AMG package, premium features, like new condition.',
                'description_ar': 'باقة إيه إم جي، كماليات فاخرة، بحالة الزيرو.',
                'location': 'CAIRO',
                'seller': dealer,
                'status': 'ACTIVE'
            },
            {
                'trim': trims[5],  # Hyundai Elantra
                'price': Decimal('280000'),
                'odometer': 42000,
                'color': 'Gray',
                'color': 'Gray',
                'description_en': 'Reliable daily driver, excellent fuel economy, well maintained.',
                'description_ar': 'سيارة اعتمادية للاستخدام اليومي، استهلاك بنزين ممتاز، صيانة دورية.',
                'location': 'ALEX',
                'seller': admin,
                'status': 'ACTIVE'
            },
        ]
        
        for listing_data in listings_data:
            listing, created = Listing.objects.get_or_create(
                trim=listing_data['trim'],
                seller=listing_data['seller'],
                defaults=listing_data
            )
            if created:
                self.stdout.write(f'✓ Created listing: {listing.trim} - {listing.price} EGP')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Sample data populated successfully!'))
        self.stdout.write(self.style.WARNING('\nTest Accounts:'))
        self.stdout.write('  Admin: admin / admin123')
        self.stdout.write('  Dealer: dealer1 / dealer123')
        self.stdout.write(f'\nCreated {Make.objects.count()} makes, {Model.objects.count()} models,')
        self.stdout.write(f'{CarTrim.objects.count()} trims, and {Listing.objects.count()} listings.')

# Abo Raaya Motors - Premium Car Marketplace

A bilingual (Arabic/English) car sales marketplace built with Django 5, featuring 3D visual effects, glassmorphism UI, and advanced cascading dropdown system.

## Features

- ✨ **Premium UI/UX**: Three.js particle effects, GSAP animations, glassmorphism design
- 🌍 **Fully Bilingual**: Arabic (RTL) and English (LTR) support
- 🚗 ** Smart Car Selection**: Cascading dropdowns (Make → Model → Trim) to prevent user errors
- 🖼️ **Auto Image Compression**: Server-side WebP conversion and resizing
- 📊 **Smart Badges**: Auto-generated badges (Fuel Saver, High Performance) based on specs
- 👥 **Dealer Verification**: Egyptian compliance (Commercial Registry, Tax Card)
- 📱 **Fully Responsive**: Mobile-first design with Bootstrap 5

## Quick Start

### Prerequisites

- Python 3.10+
- pip
- Virtual environment (recommended)

### Installation

1. **Clone/Navigate to project**:
   ```bash
   cd "/Users/elamir/Desktop/Abo Raaya Project"
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create .env file** (copy from .env.example):
   ```bash
   cp .env.example .env
   ```

5. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   - Homepage: http://127.0.0.1:8000/ar/ (Arabic) or http://127.0.0.1:8000/en/ (English)
   - Admin Panel: http://127.0.0.1:8000/admin/

## Project Structure

```
aboraaya_project/
├── core/                   # Main application
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── forms.py           # Form definitions
│   ├── urls.py            # URL routing
│   └── admin.py           # Admin configuration
├── templates/             # HTML templates
│   ├── base.html         # Base layout
│   ├── home.html         # Homepage
│   ├── listing_detail.html
│   ├── listing_form.html
│   ├── search.html
│   └── dashboard.html
├── static/               # Static assets
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript files
│   └── images/          # Static images
├── media/               # User uploads
│   ├── logos/          # Car brand logos
│   ├── cars/           # Car listing images
│   └── private/docs/   # Dealer documents
└── aboraaya_project/    # Project settings
    ├── settings.py
    └── urls.py
```

## Tech Stack

**Backend**:
- Django 5.2
- Python 3.11
- SQLite (development) / PostgreSQL (production)
- Pillow (image processing)

**Frontend**:
- Bootstrap 5.3 (RTL/LTR)
- Three.js (3D effects)
- GSAP (animations)
- Vanilla JavaScript

## Development

### Adding Sample Data

1. Login to admin panel
2. Add Makes (e.g., Toyota, BMW, Mercedes)
3. Add Models for each Make
4. Add CarTrims with specifications
5. Create sample listings

### Running Tests

```bash
python manage.py test
```

## Deployment (Hostinger)

See deployment documentation for production setup with PostgreSQL, Gunicorn, and static file configuration.

## License

Proprietary - All rights reserved

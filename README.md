# RENTPLAY v2.0 - Multi-Vendor Real Estate Marketplace

Django-based real estate platform with multi-agency support, Arabic/English bilingual, role-based dashboards, REST API, and advanced property management.

---

## What's New in v2.0

### Bug Fixes
- Fixed Property.save() forcing is_published=True (now users control publishing)
- Fixed Booking duration calculation robustness
- Migrated unique_together to UniqueConstraint (modern Django syntax)
- Removed hardcoded AWS credentials (now uses environment variables)
- Fixed admin path checking in middleware and context processors
- Fixed middleware role checking for superuser access
- Fixed 0002_banner.py migration date

### New Features
- **REST API** - Full API with filtering, searching, and pagination
- **Property Comparison** - Compare up to 3 properties side by side
- **Dynamic Sitemap.xml** - Auto-generated sitemap for SEO
- **JSON-LD Structured Data** - Schema.org markup for properties and agencies
- **Social Sharing** - Share properties on WhatsApp, Facebook, Twitter
- **Sort Options** - Sort properties by newest, price (low/high), most viewed
- **Print Support** - Print-friendly property details page
- **Video Upload** - Upload multiple videos per property
- **District AJAX Loader** - Dynamic district loading based on city selection
- **Booking Duration Calculator** - Auto-calculate rental duration
- **Password Strength Meter** - Visual password strength indicator
- **Back to Top Button** - Floating scroll-to-top button
- **Page Loader** - Smooth loading animation
- **Skeleton Loading** - Animated placeholders while content loads

### Security Improvements
- AWS credentials now use environment variables
- Conditional S3/Local storage fallback
- Added django-cors-headers for API security
- Enhanced logging with rotation
- Added file upload size limits

### UI/UX Improvements
- Chat/Messaging styles added
- Notification styles added
- Wishlist button styles added
- Status badge styles added
- Rating & review styles added
- Gallery controls improved
- Sort bar styles added
- Print styles added
- Mobile overlay handler
- Form validation enhancements
- Lazy loading for images
- Video upload preview

---

## System Requirements

- Python 3.10, 3.11, or 3.12
- pip (Python package manager)
- 500 MB free disk space

---

## Step-by-Step Setup (Windows)

### Step 1: Extract the ZIP file

Extract `rentplay_v2.0.zip` to any folder, e.g.:
```
C:\Users\hp\Downloads\rentplay_v2.0\
```

### Step 2: Create Virtual Environment

Open **Command Prompt (cmd)** or **PowerShell** and run:

```cmd
cd C:\Users\hp\Downloads\rentplay_v2.0
python -m venv venv
```

### Step 3: Activate Virtual Environment

```cmd
venv\Scripts\activate
```

You will see `(venv)` at the start of your command prompt.

### Step 4: Install Dependencies

```cmd
pip install -r requirements.txt
```

### Step 5: Create Database Tables

```cmd
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Admin User

```cmd
python manage.py createsuperuser
```

Enter the following when prompted:
- Username: `admin`
- Email: `admin@rentplay.sa`
- Password: `admin123`

### Step 7: Load Demo Data (Optional)

```cmd
python manage.py init_demo_data
```

### Step 8: Collect Static Files

```cmd
python manage.py collectstatic --noinput
```

### Step 9: Run the Server

```cmd
python manage.py runserver
```

Open your browser to: **http://127.0.0.1:8000/**

---

## Environment Variables (Production)

Create a `.env` file in the project root:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
DATABASE_URL=postgres://user:password@localhost:5432/rentplay

# DigitalOcean Spaces (optional - falls back to local storage if not set)
DO_SPACES_KEY=your-spaces-key
DO_SPACES_SECRET=your-spaces-secret
DO_SPACES_BUCKET=your-bucket-name
DO_SPACES_ENDPOINT=https://your-region.digitaloceanspaces.com

# Google Maps
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

---

## Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Super Admin | admin | admin123 |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/properties/ | GET | List all properties (with filter, sort, search) |
| /api/properties/<id>/ | GET | Get property details |
| /api/properties/<id>/reviews/ | GET | Get property reviews |
| /api/agencies/ | GET | List all agencies |
| /api/agencies/<slug>/ | GET | Get agency details |
| /api/types/ | GET | List property types |
| /api/cities/ | GET | List cities |
| /api/bookings/ | POST | Create a booking |

---

## Language Switching

- **Arabic (default):** The site loads in Arabic (RTL layout)
- **English:** Click the globe icon in the navbar to switch

The language is saved in your browser session.

---

## Project Structure

```
rentplay_v2.0/
├── config/              # Django settings and config
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── rentplay/            # Main application
│   ├── __init__.py
│   ├── admin.py
│   ├── api_views.py     # REST API views
│   ├── apps.py
│   ├── context_processors.py
│   ├── forms.py
│   ├── middleware.py
│   ├── models.py
│   ├── serializers.py   # DRF serializers
│   ├── signals.py
│   ├── urls.py
│   ├── views.py
│   └── migrations/
│       ├── __init__.py
│       ├── 0001_initial.py
│       └── 0002_banner.py
├── templates/           # HTML templates
│   ├── base/
│   ├── agency/
│   ├── dashboard/
│   ├── properties/
│   └── registration/
├── static/              # CSS, JS, images
│   ├── css/
│   ├── js/
│   └── images/
├── manage.py
├── requirements.txt
├── init_demo_data.py
└── README.md
```

---

## Support

For issues, check the logs at `logs/django.log`.

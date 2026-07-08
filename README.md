# RENTPLAY v2.0 - Multi-Vendor Real Estate Marketplace

Django-based real estate platform with multi-agency support, Arabic/English bilingual, role-based dashboards, REST API, and advanced property management.

**Live URLs:**
- Custom Domain: https://rentplay.net
- App Platform: https://rentplay-lrtcf.ondigitalocean.app/
- GitHub: https://github.com/kerolestharwat83-cyber/RENTPLAY

---

## What's New in v2.0

### Bug Fixes
- Fixed Property.save() forcing is_published=True (now users control publishing)
- Fixed Booking duration calculation robustness
- Migrated unique_together to UniqueConstraint (modern Django syntax)
- Removed hardcoded credentials (now uses environment variables)
- Fixed admin path checking in middleware and context processors
- Fixed middleware role checking for superuser access
- Fixed MEDIA_URL double-definition bug
- Added PostgreSQL SSL support

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
- All credentials moved to environment variables
- Conditional S3/Local storage fallback
- SSL redirect support for production
- Secure cookie settings
- Enhanced logging with rotation

---

## Quick Start (Local Development)

```bash
# 1. Extract the ZIP
cd rentplay_v2.0/project

# 2. Create virtual environment
python -m venv venv

# 3. Activate (Windows)
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create database
python manage.py makemigrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Load demo data (optional)
python manage.py init_demo_data

# 8. Collect static
python manage.py collectstatic --noinput

# 9. Run server
python manage.py runserver
```

Or simply double-click `run.bat` on Windows!

---

## Environment Variables

All sensitive configuration is read from environment variables. **Never hardcode credentials in your code.**

Create a `.env` file locally or set variables in your hosting platform.

### Required Variables

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Long random string (50+ chars). Generate: `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DEBUG` | `True` for development, `False` for production |
| `ALLOWED_HOSTS` | Comma-separated domains |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated HTTPS origins |
| `DATABASE_URL` | Database connection string |
| `ADMIN_URL` | Random string to hide admin panel URL |

### Optional Variables (for DigitalOcean Spaces file storage)

| Variable | Description |
|----------|-------------|
| `DO_SPACES_KEY` | Spaces Access Key |
| `DO_SPACES_SECRET` | Spaces Secret Key |
| `DO_SPACES_BUCKET` | Spaces bucket name |
| `DO_SPACES_ENDPOINT` | Spaces endpoint URL |

### Optional Security Variables

| Variable | Description |
|----------|-------------|
| `SECURE_SSL_REDIRECT` | `True` to force HTTPS |
| `SESSION_COOKIE_SECURE` | `True` for HTTPS-only session cookies |
| `CSRF_COOKIE_SECURE` | `True` for HTTPS-only CSRF cookies |

See `.env.example` file for a template.

---

## Build & Run Commands (DigitalOcean App Platform)

### Build Command:
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

### Run Command:
```bash
gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 config.wsgi:application
```

### First-Time Setup (Console):
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py init_demo_data
```

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
| /sitemap.xml | GET | Dynamic sitemap for SEO |

---

## Admin Panel

The admin panel is hidden at a custom URL for security:
```
https://rentplay.net/YOUR_ADMIN_URL/
```
Replace `YOUR_ADMIN_URL` with the value you set in the `ADMIN_URL` environment variable.

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
├── rentplay/            # Main application + API + Serializers
├── templates/           # HTML templates (25+ templates)
├── static/              # CSS + JS + Images
├── manage.py            # Django manager
├── requirements.txt     # Dependencies
├── init_demo_data.py    # Demo data
├── run.bat              # One-click Windows runner
├── Dockerfile           # Docker container
├── .env.example         # Environment variables template
├── README.md            # This file
└── GUIDE.md             # Detailed deployment guide
```

---

## Support

For issues, check the logs at `logs/django.log`.

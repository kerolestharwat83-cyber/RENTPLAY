"""
RENTPLAY Context Processors v2.0
Safe for all templates including Django Admin
"""

from django.conf import settings


def site_settings(request):
    """Site-wide settings - SAFE for admin"""
    admin_path = f'/{getattr(settings, "ADMIN_URL", "a7x9k2m1")}/'
    if request.path.startswith(admin_path):
        return {}
    return {
        'SITE_NAME': 'RENTPLAY',
        'LANGUAGES': settings.LANGUAGES,
    }


def user_role(request):
    """User role flags - SAFE for admin"""
    admin_path = f'/{getattr(settings, "ADMIN_URL", "a7x9k2m1")}/'
    if request.path.startswith(admin_path):
        return {}

    user = request.user
    if not user.is_authenticated:
        return {
            'user_is_superadmin': False,
            'user_is_agency_admin': False,
            'user_is_agency_staff': False,
            'user_is_regular_user': True,
            'user_can_access_admin': False,
            'user_agency': None,
            'unread_notifications': 0,
        }

    is_superadmin = getattr(user, 'is_superadmin', False)
    is_agency_admin = getattr(user, 'is_agency_admin', False)
    is_agency_staff = getattr(user, 'is_agency_staff', False)
    is_agency_member = is_agency_admin or is_agency_staff
    unread = user.unread_notifications_count() if hasattr(user, 'unread_notifications_count') else 0

    return {
        'user_is_superadmin': is_superadmin,
        'user_is_agency_admin': is_agency_admin,
        'user_is_agency_staff': is_agency_staff,
        'user_is_regular_user': getattr(user, 'is_regular_user', True),
        'user_can_access_admin': is_superadmin or is_agency_member,
        'user_agency': getattr(user, 'agency', None),
        'unread_notifications': unread,
    }


def seo_context(request):
    """SEO context for templates"""
    admin_path = f'/{getattr(settings, "ADMIN_URL", "a7x9k2m1")}/'
    if request.path.startswith(admin_path):
        return {}
    return {
        'seo_title': getattr(request, 'seo_title', 'RENTPLAY'),
        'seo_description': getattr(request, 'seo_description', ''),
        'seo_image': getattr(request, 'seo_image', ''),
        'seo_url': getattr(request, 'seo_url', ''),
    }

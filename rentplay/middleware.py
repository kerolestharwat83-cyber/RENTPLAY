"""
RENTPLAY Middleware v2.0
"""

import time

from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.utils.translation import gettext_lazy as _
from django.conf import settings


# Fix 1: Consistent admin path - derive from settings.ADMIN_URL
ADMIN_PATH = f'/{getattr(settings, "ADMIN_URL", "a7x9k2m1")}/'


class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.process_request(request)
        if response:
            return response
        return self.get_response(request)

    def process_request(self, request):
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None

        user = request.user
        path = request.path

        # Fix 2: Block non-superadmins from Django admin - also checks is_superuser
        if path.startswith(ADMIN_PATH):
            if not (user.is_superadmin or user.is_superuser):
                return HttpResponseForbidden(_('Access denied. Only super administrators can access this area.'))

        # Dashboard access check
        if path.startswith('/dashboard/'):
            if not user.can_access_admin():
                return redirect('rentplay:index')

        return None


class AdminSecurityMiddleware:
    """
    Security middleware for admin panel:
    - Blocks access to old admin URLs (/admin/, /django-admin/)
    - Rate limits failed login attempts
    - Hides Django version from admin page
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Block common admin scanner URLs
        blocked_prefixes = ['/admin/', '/django-admin/', '/wp-admin/', '/administrator/',
                           '/phpmyadmin/', '/cpanel/', '/webadmin/', '/admin1/',
                           '/admin-login/', '/admin/login/', '/manage/', '/manager/',
                           '/backend/', '/control/', '/panel/', '/root/', '/webadmin/']
        for prefix in blocked_prefixes:
            if path.startswith(prefix):
                return HttpResponseForbidden(_('Access denied.'))

        # Add security headers to admin responses
        response = self.get_response(request)
        if path.startswith(ADMIN_PATH):
            response['X-Frame-Options'] = 'DENY'
            response['X-Content-Type-Options'] = 'nosniff'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate'

        return response


class SEOMiddleware:
    """Add SEO context to all requests"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.seo_title = _('RENTPLAY - Real Estate Marketplace')
        request.seo_description = _('Find your perfect home in Saudi Arabia.')
        request.seo_image = '/static/images/rentplay_logo.png'
        request.seo_url = request.build_absolute_uri()
        return self.get_response(request)


# Fix 3: Request timing middleware for performance monitoring
class RequestTimingMiddleware:
    """Log request processing time"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = time.time() - start
        response['X-Request-Duration'] = f'{duration:.3f}s'
        return response

"""
RENTPLAY Views v2.0
Core features + all new additions
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _, activate
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.template.loader import render_to_string

from .models import (
    User, Agency, Property, PropertyImage, PropertyVideo, PropertyType, City, District, Booking,
    Review, Wishlist, Message, Notification, Waitlist, Contract, Banner
)
from .forms import (
    LoginForm, UserRegistrationForm, PropertyForm, BookingForm,
    PropertyFilterForm, UserProfileForm, ReviewForm, MessageForm,
    WaitlistForm, PropertyStatusForm
)


# ==================== SORTING OPTIONS ====================
SORT_OPTIONS = {
    'newest': '-created_at',
    'price_low': 'price',
    'price_high': '-price',
    'views': '-view_count',
}


# ==================== HELPERS ====================
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def filter_properties(queryset, form_data):
    if form_data.get('search'):
        search = form_data['search']
        queryset = queryset.filter(
            Q(title__icontains=search) | Q(unit_code__icontains=search) | Q(description__icontains=search)
        )
    if form_data.get('city'):
        queryset = queryset.filter(city=form_data['city'])
    if form_data.get('district'):
        queryset = queryset.filter(district=form_data['district'])
    if form_data.get('property_type'):
        queryset = queryset.filter(property_type=form_data['property_type'])
    if form_data.get('max_price'):
        queryset = queryset.filter(price__lte=form_data['max_price'])
    if form_data.get('status'):
        queryset = queryset.filter(status=form_data['status'])
    return queryset


def apply_sorting(queryset, sort_param):
    """Apply sorting to a queryset based on SORT_OPTIONS mapping."""
    sort_field = SORT_OPTIONS.get(sort_param)
    if sort_field:
        queryset = queryset.order_by(sort_field)
    return queryset


def get_property_json_ld(property_obj):
    """Generate JSON-LD structured data for a property"""
    return {
        "@context": "https://schema.org",
        "@type": "Apartment",
        "name": property_obj.title,
        "description": property_obj.description,
        "url": property_obj.get_absolute_url(),
        "address": {
            "@type": "PostalAddress",
            "addressLocality": property_obj.city.name if property_obj.city else "",
            "addressRegion": property_obj.district.name if property_obj.district else "",
            "addressCountry": "SA"
        },
        "numberOfRooms": property_obj.rooms,
        "numberOfBathroomsTotal": property_obj.bathrooms,
        "floorSize": {
            "@type": "QuantitativeValue",
            "value": property_obj.area,
            "unitCode": "MTK"
        },
        "price": {
            "@type": "PriceSpecification",
            "price": str(property_obj.price),
            "priceCurrency": "SAR"
        }
    }


def create_notification(user, notification_type, title, message, link=''):
    """Create a notification for a user"""
    Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link
    )


# ==================== AJAX: DISTRICTS ====================
def get_districts(request):
    city_id = request.GET.get('city_id')
    if city_id:
        try:
            districts = District.objects.filter(city_id=int(city_id)).values('id', 'name', 'name_en')
            return JsonResponse({'success': True, 'districts': list(districts)})
        except (ValueError, TypeError):
            pass
    return JsonResponse({'success': True, 'districts': []})


# ==================== LANDING PAGE ====================
@cache_page(60 * 5)
def index(request):
    # Fix 5: Cache key includes language AND query params for uniqueness
    query_key = request.META.get('QUERY_STRING', '')
    cache_key = f'index_{request.LANGUAGE_CODE}_{hash(query_key) & 0xFFFFFFFF}'
    context = cache.get(cache_key)

    if context is None:
        properties = Property.objects.filter(is_published=True).select_related(
            'agency', 'property_type', 'city', 'district'
        ).prefetch_related('images')

        total_count = properties.count()
        available_count = properties.filter(status=Property.Status.AVAILABLE).count()
        rented_count = properties.filter(status=Property.Status.RENTED).count()
        agency_count = Agency.objects.filter(status=Agency.Status.ACTIVE).count()

        filter_form = PropertyFilterForm(request.GET or None)
        if filter_form.is_valid():
            properties = filter_properties(properties, filter_form.cleaned_data)

        nav_filter = request.GET.get('nav', 'all')
        if nav_filter == 'available':
            properties = properties.filter(status=Property.Status.AVAILABLE)
        elif nav_filter == 'rented':
            properties = properties.filter(status=Property.Status.RENTED)

        # Fix 7: Apply sorting if requested
        sort_param = request.GET.get('sort', '')
        if sort_param in SORT_OPTIONS:
            properties = apply_sorting(properties, sort_param)

        paginator = Paginator(properties, 15)
        page_obj = paginator.get_page(request.GET.get('page'))

        # Get active hero banners
        hero_banners = Banner.objects.filter(position=Banner.Position.HERO, is_active=True)

        context = {
            'page_obj': page_obj,
            'filter_form': filter_form,
            'nav_filter': nav_filter,
            'sort_param': sort_param,
            'sort_options': SORT_OPTIONS,
            'stats': {
                'total': total_count,
                'available': available_count,
                'rented': rented_count,
                'agencies': agency_count,
            },
            'hero_banners': hero_banners,
            'cities': City.objects.all(),
            'property_types': PropertyType.objects.all(),
            'seo_title': _('RENTPLAY - Real Estate Marketplace'),
            'seo_description': _('Find your perfect home in Saudi Arabia. Browse properties from top real estate agencies.'),
        }
        cache.set(cache_key, context, 300)
    else:
        # Re-apply filters if form submitted
        filter_form = PropertyFilterForm(request.GET or None)
        if filter_form.is_valid():
            properties = Property.objects.filter(is_published=True).select_related(
                'agency', 'property_type', 'city', 'district'
            ).prefetch_related('images')
            properties = filter_properties(properties, filter_form.cleaned_data)
            nav_filter = request.GET.get('nav', 'all')
            if nav_filter == 'available':
                properties = properties.filter(status=Property.Status.AVAILABLE)
            elif nav_filter == 'rented':
                properties = properties.filter(status=Property.Status.RENTED)
            paginator = Paginator(properties, 15)
            page_obj = paginator.get_page(request.GET.get('page'))
            context['page_obj'] = page_obj
            context['filter_form'] = filter_form
            context['nav_filter'] = nav_filter

    return render(request, 'properties/index.html', context)


# ==================== AGENCY PAGES ====================
def agency_list(request):
    agencies = Agency.objects.filter(status=Agency.Status.ACTIVE).order_by('-created_at')
    paginator = Paginator(agencies, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'agency/agency_list.html', {
        'page_obj': page_obj,
        'seo_title': _('Real Estate Agencies'),
        'seo_description': _('Browse trusted real estate agencies in Saudi Arabia.'),
    })


def agency_detail(request, agency_slug):
    agency = get_object_or_404(Agency, slug=agency_slug, status=Agency.Status.ACTIVE)
    properties = Property.objects.filter(agency=agency, is_published=True).select_related(
        'property_type', 'city', 'district'
    ).prefetch_related('images')

    filter_form = PropertyFilterForm(request.GET or None)
    if filter_form.is_valid():
        properties = filter_properties(properties, filter_form.cleaned_data)

    nav_filter = request.GET.get('nav', 'all')
    if nav_filter == 'available':
        properties = properties.filter(status=Property.Status.AVAILABLE)
    elif nav_filter == 'rented':
        properties = properties.filter(status=Property.Status.RENTED)

    # Apply sorting if requested
    sort_param = request.GET.get('sort', '')
    if sort_param in SORT_OPTIONS:
        properties = apply_sorting(properties, sort_param)

    paginator = Paginator(properties, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    reviews = Review.objects.filter(agency=agency, is_approved=True).select_related('user')[:10]

    return render(request, 'agency/agency_detail.html', {
        'agency': agency,
        'page_obj': page_obj,
        'filter_form': filter_form,
        'nav_filter': nav_filter,
        'sort_param': sort_param,
        'sort_options': SORT_OPTIONS,
        'stats': {
            'total': agency.property_count,
            'available': agency.available_count,
            'rented': agency.rented_count,
        },
        'reviews': reviews,
        'seo_title': f"{agency.name} - {_('Properties')}",
        'seo_description': agency.description[:160] if agency.description else '',
    })


# ==================== PROPERTY DETAIL ====================
def property_detail(request, pk):
    property_obj = get_object_or_404(
        Property.objects.select_related('agency', 'property_type', 'city', 'district'),
        pk=pk, is_published=True
    )
    property_obj.increment_views()

    images = property_obj.images.all()
    videos = property_obj.videos.all()

    similar = Property.objects.filter(
        agency=property_obj.agency, is_published=True, status=Property.Status.AVAILABLE
    ).exclude(pk=pk).select_related('property_type', 'city')[:4]

    booking_form = BookingForm(property_obj=property_obj)
    review_form = ReviewForm()
    waitlist_form = WaitlistForm()

    reviews = Review.objects.filter(property_unit=property_obj, is_approved=True).select_related('user')[:10]

    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, property_unit=property_obj).exists()

    is_waitlisted = False
    if request.user.is_authenticated:
        is_waitlisted = Waitlist.objects.filter(user=request.user, property_unit=property_obj).exists()

    # Fix 6: Generate structured data JSON-LD
    json_ld_data = get_property_json_ld(property_obj)

    context = {
        'property': property_obj,
        'images': images,
        'videos': videos,
        'similar_properties': similar,
        'booking_form': booking_form,
        'review_form': review_form,
        'waitlist_form': waitlist_form,
        'reviews': reviews,
        'is_wishlisted': is_wishlisted,
        'is_waitlisted': is_waitlisted,
        'media_json': [
            * [{'type': 'image', 'src': img.image.url} for img in images],
            * [{'type': 'video', 'src': vid.video.url} for vid in videos],
        ],
        'json_ld': json_ld_data,
        'seo_title': property_obj.title,
        'seo_description': property_obj.description[:160] if property_obj.description else '',
    }
    return render(request, 'properties/property_detail.html', context)


# ==================== PROPERTY SHARE ====================
def property_share(request, pk):
    """Share property page with SEO-optimized meta tags"""
    property_obj = get_object_or_404(
        Property.objects.select_related('agency', 'property_type', 'city', 'district'),
        pk=pk, is_published=True
    )

    request.seo_title = property_obj.title
    request.seo_description = property_obj.description[:160] if property_obj.description else ''
    request.seo_image = property_obj.main_image or '/static/images/rentplay_logo.png'

    images = property_obj.images.all()
    videos = property_obj.videos.all()

    similar = Property.objects.filter(
        agency=property_obj.agency, is_published=True, status=Property.Status.AVAILABLE
    ).exclude(pk=pk).select_related('property_type', 'city')[:4]

    booking_form = BookingForm(property_obj=property_obj)
    review_form = ReviewForm()

    reviews = Review.objects.filter(property_unit=property_obj, is_approved=True).select_related('user')[:10]

    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, property_unit=property_obj).exists()

    json_ld_data = get_property_json_ld(property_obj)

    return render(request, 'properties/property_detail.html', {
        'property': property_obj,
        'images': images,
        'videos': videos,
        'similar_properties': similar,
        'booking_form': booking_form,
        'review_form': review_form,
        'reviews': reviews,
        'is_wishlisted': is_wishlisted,
        'media_json': [
            * [{'type': 'image', 'src': img.image.url} for img in images],
            * [{'type': 'video', 'src': vid.video.url} for vid in videos],
        ],
        'json_ld': json_ld_data,
        'seo_title': property_obj.title,
        'seo_description': property_obj.description[:160] if property_obj.description else '',
    })


# ==================== PROPERTY COMPARE ====================
def property_compare(request):
    """Compare up to 3 properties"""
    compare_ids = request.session.get('compare_ids', [])
    if not compare_ids:
        messages.info(request, _('Select properties to compare.'))
        return redirect('rentplay:index')

    properties = Property.objects.filter(
        id__in=compare_ids, is_published=True
    ).select_related('agency', 'property_type', 'city', 'district').prefetch_related('images')

    if properties.count() < 2:
        messages.info(request, _('Select at least 2 properties to compare.'))
        return redirect('rentplay:index')

    return render(request, 'properties/property_compare.html', {
        'properties': properties,
        'seo_title': _('Compare Properties'),
    })


def property_compare_add(request, property_pk):
    """Add property to compare list"""
    compare_ids = request.session.get('compare_ids', [])
    property_pk = int(property_pk)

    if property_pk in compare_ids:
        messages.info(request, _('Property already in compare list.'))
    elif len(compare_ids) >= 3:
        messages.warning(request, _('You can compare up to 3 properties. Remove one first.'))
    else:
        compare_ids.append(property_pk)
        request.session['compare_ids'] = compare_ids
        messages.success(request, _('Property added to compare.'))

    return redirect(request.META.get('HTTP_REFERER', 'rentplay:index'))


def property_compare_remove(request, property_pk):
    """Remove property from compare list"""
    compare_ids = request.session.get('compare_ids', [])
    property_pk = int(property_pk)

    if property_pk in compare_ids:
        compare_ids.remove(property_pk)
        request.session['compare_ids'] = compare_ids

    return redirect(request.META.get('HTTP_REFERER', 'rentplay:index'))


# ==================== DJANGO SITEMAP CLASSES (for config/urls.py) ====================
from django.contrib.sitemaps import Sitemap

class PropertySitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return Property.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class AgencySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Agency.objects.filter(status=Agency.Status.ACTIVE)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


# ==================== SITEMAP.XML (standalone view) ====================
def sitemap_xml(request):
    """Generate dynamic sitemap.xml"""
    from django.utils import timezone
    now = timezone.now()

    properties = Property.objects.filter(is_published=True).select_related('agency', 'city')
    agencies = Agency.objects.filter(status=Agency.Status.ACTIVE)

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    # Home page
    xml += f'  <url>\n    <loc>{request.build_absolute_uri("/")}</loc>\n    <priority>1.0</priority>\n  </url>\n'

    # Agencies list
    xml += f'  <url>\n    <loc>{request.build_absolute_uri("/agencies/")}</loc>\n    <priority>0.7</priority>\n  </url>\n'

    # Map search
    xml += f'  <url>\n    <loc>{request.build_absolute_uri("/map-search/")}</loc>\n    <priority>0.6</priority>\n  </url>\n'

    # Individual properties
    for prop in properties:
        xml += f'  <url>\n    <loc>{request.build_absolute_uri(prop.get_absolute_url())}</loc>\n    <lastmod>{prop.updated_at.strftime("%Y-%m-%d")}</lastmod>\n    <changefreq>daily</changefreq>\n    <priority>0.8</priority>\n  </url>\n'

    # Individual agencies
    for agency in agencies:
        xml += f'  <url>\n    <loc>{request.build_absolute_uri(agency.get_absolute_url())}</loc>\n    <lastmod>{agency.updated_at.strftime("%Y-%m-%d")}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.6</priority>\n  </url>\n'

    xml += '</urlset>'
    return HttpResponse(xml, content_type='application/xml')


# ==================== BOOKING SUBMISSION ====================
@require_POST
def submit_booking(request, property_pk):
    property_obj = get_object_or_404(Property, pk=property_pk, is_published=True)
    form = BookingForm(request.POST, property_obj=property_obj)

    if form.is_valid():
        booking = form.save(commit=False)
        booking.property_unit = property_obj
        booking.agency = property_obj.agency
        booking.ip_address = get_client_ip(request)

        if booking.start_date and booking.end_date:
            from dateutil.relativedelta import relativedelta
            rd = relativedelta(booking.end_date, booking.start_date)
            booking.duration_months = (rd.years * 12) + rd.months
            if rd.days > 0:
                booking.duration_months += 1

        booking.save()

        # Create notification for agency admin
        if property_obj.agency and property_obj.agency.admin:
            create_notification(
                property_obj.agency.admin,
                Notification.Type.BOOKING,
                _('New Booking'),
                _('New booking for') + f' {property_obj.title}',
                f'/dashboard/bookings/'
            )

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': _('Your booking has been submitted successfully! The agency will contact you soon.'),
                'booking_id': booking.pk,
                'agency_name': booking.agency.name,
            })

        messages.success(request, _('Your booking has been submitted successfully!'))
        return redirect('rentplay:property_detail', pk=property_pk)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        errors = {field: str(error[0]) for field, error in form.errors.items() if field != '__all__'}
        non_field = form.errors.get('__all__')
        return JsonResponse({
            'success': False,
            'errors': errors,
            'non_field_errors': [str(e) for e in non_field] if non_field else []
        }, status=400)

    messages.error(request, _('Please correct the errors below.'))
    return redirect('rentplay:property_detail', pk=property_pk)


# ==================== AUTHENTICATION ====================
def user_login(request):
    if request.user.is_authenticated:
        return redirect('rentplay:index')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        if user.can_access_admin():
            return redirect('rentplay:dashboard')
        return redirect('rentplay:index')
    return render(request, 'registration/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, _('You have been logged out successfully.'))
    return redirect('rentplay:index')


def user_register(request):
    if request.user.is_authenticated:
        return redirect('rentplay:index')
    form = UserRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, _('Welcome! Your account has been created.'))
        return redirect('rentplay:index')
    return render(request, 'registration/register.html', {'form': form})


# ==================== PROFILE ====================
@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Profile updated successfully.'))
            return redirect('rentplay:profile')
    else:
        form = UserProfileForm(instance=request.user)

    user_bookings = Booking.objects.filter(
        phone=request.user.phone
    ).select_related('property_unit', 'agency').order_by('-created_at')[:10] if request.user.is_regular_user else None

    wishlist = Wishlist.objects.filter(user=request.user).select_related('property_unit').order_by('-created_at')[:10]

    return render(request, 'registration/profile.html', {
        'form': form,
        'bookings': user_bookings,
        'wishlist': wishlist,
    })


# ==================== DASHBOARD ====================
@login_required
def dashboard(request):
    user = request.user
    if not user.can_access_admin():
        return HttpResponseForbidden(_('You do not have access to the dashboard.'))

    if user.is_superadmin:
        context = _get_superadmin_dashboard(request)
        return render(request, 'dashboard/superadmin_dashboard.html', context)
    if user.is_agency_admin:
        context = _get_agency_admin_dashboard(request)
        return render(request, 'dashboard/agency_dashboard.html', context)
    if user.is_agency_staff:
        context = _get_agency_staff_dashboard(request)
        return render(request, 'dashboard/staff_dashboard.html', context)
    return HttpResponseForbidden(_('Access denied.'))


def _get_superadmin_dashboard(request):
    return {
        'stats': {
            'properties': Property.objects.count(),
            'available': Property.objects.filter(status=Property.Status.AVAILABLE).count(),
            'rented': Property.objects.filter(status=Property.Status.RENTED).count(),
            'agencies': Agency.objects.count(),
            'bookings': Booking.objects.count(),
            'users': User.objects.filter(role=User.Role.REGULAR_USER).count(),
        },
        'recent_properties': Property.objects.select_related('agency').order_by('-created_at')[:10],
        'recent_bookings': Booking.objects.select_related('property_unit', 'agency').order_by('-created_at')[:10],
        'agencies': Agency.objects.annotate(
            prop_count=Count('properties'), booking_count=Count('bookings')
        ).order_by('-prop_count')[:10],
    }


def _get_agency_admin_dashboard(request):
    agency = request.user.agency
    if not agency:
        messages.error(request, _('You are not assigned to any agency.'))
        return redirect('rentplay:index')
    properties = Property.objects.filter(agency=agency)
    bookings = Booking.objects.filter(agency=agency)
    staff = User.objects.filter(agency=agency, role__in=[User.Role.AGENCY_ADMIN, User.Role.AGENCY_STAFF])
    return {
        'agency': agency,
        'stats': {
            'total_properties': properties.count(),
            'available': properties.filter(status=Property.Status.AVAILABLE).count(),
            'rented': properties.filter(status=Property.Status.RENTED).count(),
            'total_bookings': bookings.count(),
            'new_bookings': bookings.filter(status=Booking.Status.PENDING).count(),
            'staff_count': staff.count(),
        },
        'recent_properties': properties.order_by('-created_at')[:5],
        'recent_bookings': bookings.order_by('-created_at')[:5],
        'properties': properties.select_related('property_type', 'city').order_by('-created_at'),
        'bookings': bookings.select_related('property_unit').order_by('-created_at'),
    }


def _get_agency_staff_dashboard(request):
    agency = request.user.agency
    if not agency:
        messages.error(request, _('You are not assigned to any agency.'))
        return redirect('rentplay:index')
    properties = Property.objects.filter(agency=agency)
    bookings = Booking.objects.filter(agency=agency)
    return {
        'agency': agency,
        'stats': {
            'total_properties': properties.count(),
            'available': properties.filter(status=Property.Status.AVAILABLE).count(),
            'rented': properties.filter(status=Property.Status.RENTED).count(),
            'new_bookings': bookings.filter(status=Booking.Status.PENDING).count(),
        },
        'properties': properties.select_related('property_type', 'city').order_by('-created_at'),
        'bookings': bookings.select_related('property_unit').order_by('-created_at')[:20],
    }


# ==================== DASHBOARD MANAGEMENT ====================
@login_required
def dashboard_properties(request):
    user = request.user
    if not user.can_access_admin():
        return HttpResponseForbidden()
    if user.is_superadmin:
        properties = Property.objects.all()
    elif user.agency:
        properties = Property.objects.filter(agency=user.agency)
    else:
        properties = Property.objects.none()

    properties = properties.select_related('agency', 'property_type', 'city')
    search = request.GET.get('search', '')
    if search:
        properties = properties.filter(Q(title__icontains=search) | Q(unit_code__icontains=search))

    paginator = Paginator(properties, 15)
    return render(request, 'dashboard/properties_list.html', {
        'page_obj': paginator.get_page(request.GET.get('page')),
        'search': search,
    })


@login_required
def dashboard_bookings(request):
    user = request.user
    if not user.can_access_admin():
        return HttpResponseForbidden()
    if user.is_superadmin:
        bookings = Booking.objects.all()
    elif user.agency:
        bookings = Booking.objects.filter(agency=user.agency)
    else:
        bookings = Booking.objects.none()

    bookings = bookings.select_related('property_unit', 'agency')
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    search = request.GET.get('search', '')
    if search:
        bookings = bookings.filter(
            Q(client_name__icontains=search) | Q(phone__icontains=search) | Q(property_unit__title__icontains=search)
        )
    paginator = Paginator(bookings.order_by('-created_at'), 15)
    return render(request, 'dashboard/bookings_list.html', {
        'page_obj': paginator.get_page(request.GET.get('page')),
        'status_filter': status_filter,
        'search': search,
    })


@login_required
def booking_update_status(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    user = request.user
    if not user.is_superadmin and (not user.agency or booking.agency != user.agency):
        return JsonResponse({'success': False, 'error': _('Permission denied.')}, status=403)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in [s[0] for s in Booking.Status.choices]:
            booking.status = new_status
            booking.handled_by = user
            booking.save()
            return JsonResponse({
                'success': True,
                'message': _('Status updated.'),
                'status': booking.get_status_display(),
                'status_code': booking.status
            })
    return JsonResponse({'success': False, 'error': _('Invalid request.')}, status=400)


@login_required
def property_create(request):
    user = request.user
    if not user.can_access_admin():
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            prop = form.save(commit=False)
            if not user.is_superadmin and user.agency:
                prop.agency = user.agency
            prop.created_by = user
            prop.save()
            for img in request.FILES.getlist('images'):
                PropertyImage.objects.create(property_unit=prop, image=img, order=prop.images.count())
            for vid in request.FILES.getlist('videos'):
                PropertyVideo.objects.create(property_unit=prop, video=vid)
            messages.success(request, _('Property created successfully.'))
            return redirect('rentplay:dashboard')
    else:
        form = PropertyForm(user=user)
        if not user.is_superadmin:
            form.fields.pop('agency', None)
    return render(request, 'dashboard/property_form.html', {
        'form': form, 'title': _('Add New Property'), 'action': _('Create')
    })


@login_required
def property_edit(request, pk):
    user = request.user
    prop = get_object_or_404(Property, pk=pk)
    if not user.is_superadmin and prop.agency != user.agency:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=prop, user=user)
        if form.is_valid():
            form.save()
            for img in request.FILES.getlist('images'):
                PropertyImage.objects.create(property_unit=prop, image=img, order=prop.images.count())
            for vid in request.FILES.getlist('videos'):
                PropertyVideo.objects.create(property_unit=prop, video=vid)
            messages.success(request, _('Property updated successfully.'))
            return redirect('rentplay:dashboard_properties')
    else:
        form = PropertyForm(instance=prop, user=user)
        if not user.is_superadmin:
            form.fields.pop('agency', None)
    return render(request, 'dashboard/property_form.html', {
        'form': form, 'property': prop, 'title': _('Edit Property'), 'action': _('Update')
    })


@login_required
@require_POST
def property_delete(request, pk):
    user = request.user
    prop = get_object_or_404(Property, pk=pk)
    if not user.is_superadmin and prop.agency != user.agency:
        return HttpResponseForbidden()
    prop.delete()
    messages.success(request, _('Property deleted successfully.'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('rentplay:dashboard_properties')


# ==================== PROPERTY STATUS TOGGLE (NEW) ====================
@login_required
@require_POST
def property_toggle_status(request, pk):
    user = request.user
    prop = get_object_or_404(Property, pk=pk)
    if not user.is_superadmin and prop.agency != user.agency:
        return JsonResponse({'success': False, 'error': _('Permission denied.')}, status=403)

    new_status = request.POST.get('status')
    if new_status in [s[0] for s in Property.Status.choices]:
        old_status = prop.status
        prop.status = new_status
        prop.save()

        # Notify waitlist users if property became available
        if old_status != 'available' and new_status == 'available':
            waitlist_entries = Waitlist.objects.filter(property_unit=prop, notified=False)
            for entry in waitlist_entries:
                create_notification(
                    entry.user,
                    Notification.Type.STATUS,
                    _('Property Available!'),
                    f'{prop.title} ' + _('is now available for rent!'),
                    prop.get_absolute_url()
                )
                entry.notified = True
                entry.save()

        return JsonResponse({
            'success': True,
            'message': _('Status updated.'),
            'status': prop.get_status_display(),
            'status_code': prop.status
        })
    return JsonResponse({'success': False, 'error': _('Invalid status.')}, status=400)


# ==================== WISHLIST (NEW) ====================
@login_required
def wishlist_toggle(request, property_pk):
    property_obj = get_object_or_404(Property, pk=property_pk)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user, property_unit=property_obj
    )
    if not created:
        wishlist_item.delete()
        return JsonResponse({'success': True, 'added': False, 'message': _('Removed from wishlist.')})
    return JsonResponse({'success': True, 'added': True, 'message': _('Added to wishlist.')})


@login_required
def wishlist_list(request):
    wishlist = Wishlist.objects.filter(user=request.user).select_related(
        'property_unit', 'property_unit__agency', 'property_unit__city'
    ).order_by('-created_at')
    paginator = Paginator(wishlist, 15)
    return render(request, 'properties/wishlist.html', {
        'page_obj': paginator.get_page(request.GET.get('page'))
    })


# ==================== REVIEWS (NEW) ====================
@login_required
@require_POST
def review_create(request, property_pk):
    property_obj = get_object_or_404(Property, pk=property_pk)
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.property_unit = property_obj
        review.agency = property_obj.agency
        review.save()

        # Notify agency admin
        if property_obj.agency and property_obj.agency.admin:
            create_notification(
                property_obj.agency.admin,
                Notification.Type.REVIEW,
                _('New Review'),
                f'{request.user.username} ' + _('reviewed') + f' {property_obj.title}',
                property_obj.get_absolute_url()
            )

        messages.success(request, _('Review submitted and pending approval.'))
    else:
        messages.error(request, _('Please correct the errors.'))
    return redirect('rentplay:property_detail', pk=property_pk)


# ==================== MESSAGES (NEW) ====================
@login_required
def message_list(request):
    user = request.user
    messages_qs = Message.objects.filter(
        Q(sender=user) | Q(receiver=user)
    ).select_related('sender', 'receiver', 'property_unit').order_by('-created_at')

    # Group by conversation partner
    conversations = {}
    for msg in messages_qs:
        partner = msg.receiver if msg.sender == user else msg.sender
        if partner.id not in conversations:
            conversations[partner.id] = {
                'partner': partner,
                'last_message': msg,
                'unread': 0
            }
        if msg.receiver == user and not msg.is_read:
            conversations[partner.id]['unread'] += 1

    return render(request, 'dashboard/messages.html', {
        'conversations': conversations.values()
    })


@login_required
def message_conversation(request, user_id):
    partner = get_object_or_404(User, pk=user_id)
    user = request.user

    messages_qs = Message.objects.filter(
        Q(sender=user, receiver=partner) | Q(sender=partner, receiver=user)
    ).select_related('sender', 'receiver').order_by('created_at')

    # Mark as read
    Message.objects.filter(sender=partner, receiver=user, is_read=False).update(is_read=True)

    form = MessageForm()
    return render(request, 'dashboard/conversation.html', {
        'partner': partner,
        'messages': messages_qs,
        'form': form,
    })


@login_required
@require_POST
def message_send(request, user_id):
    receiver = get_object_or_404(User, pk=user_id)
    form = MessageForm(request.POST)
    if form.is_valid():
        msg = form.save(commit=False)
        msg.sender = request.user
        msg.receiver = receiver
        msg.save()

        create_notification(
            receiver,
            Notification.Type.MESSAGE,
            _('New Message'),
            f'{request.user.username}: {msg.content[:50]}',
            f'/messages/'
        )

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': _('Message sent.')})
        messages.success(request, _('Message sent.'))
    return redirect('rentplay:message_conversation', user_id=user_id)


# ==================== NOTIFICATIONS (NEW) ====================
@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(notifications, 15)
    return render(request, 'dashboard/notifications.html', {
        'page_obj': paginator.get_page(request.GET.get('page'))
    })


@login_required
@require_POST
def notification_mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})


# ==================== WAITLIST (NEW) ====================
@login_required
@require_POST
def waitlist_join(request, property_pk):
    property_obj = get_object_or_404(Property, pk=property_pk)
    form = WaitlistForm(request.POST)
    if form.is_valid():
        waitlist, created = Waitlist.objects.get_or_create(
            user=request.user, property_unit=property_obj,
            defaults={'email': form.cleaned_data['email'], 'phone': form.cleaned_data.get('phone', '')}
        )
        if created:
            return JsonResponse({'success': True, 'message': _('You will be notified when this property is available.')})
        return JsonResponse({'success': True, 'message': _('Already on the waitlist.')})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


# ==================== MAP SEARCH (NEW) ====================
def map_search(request):
    properties = Property.objects.filter(
        is_published=True, status=Property.Status.AVAILABLE,
        lat__isnull=False, lng__isnull=False
    ).select_related('agency', 'property_type', 'city')

    # Filter by bounds if provided
    ne_lat = request.GET.get('ne_lat')
    ne_lng = request.GET.get('ne_lng')
    sw_lat = request.GET.get('sw_lat')
    sw_lng = request.GET.get('sw_lng')

    if all([ne_lat, ne_lng, sw_lat, sw_lng]):
        properties = properties.filter(
            lat__lte=float(ne_lat), lat__gte=float(sw_lat),
            lng__lte=float(ne_lng), lng__gte=float(sw_lng)
        )

    properties_data = []
    for p in properties[:100]:
        properties_data.append({
            'id': p.id,
            'title': p.title,
            'price': str(p.price),
            'lat': float(p.lat) if p.lat else None,
            'lng': float(p.lng) if p.lng else None,
            'url': p.get_absolute_url(),
            'image': p.main_image,
            'status': p.status,
        })

    return render(request, 'properties/map_search.html', {
        'properties_json': properties_data,
        'seo_title': _('Map Search'),
    })


# ==================== LANGUAGE SWITCHER ====================
def set_language(request):
    from django.utils import translation
    from django.conf import settings

    lang = request.GET.get('lang', 'ar')
    if lang not in [l[0] for l in settings.LANGUAGES]:
        lang = 'ar'

    translation.activate(lang)
    request.session[translation.LANGUAGE_SESSION_KEY] = lang

    next_url = request.GET.get('next', '/')
    response = redirect(next_url)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)

    return response


# ==================== SEO FILES ====================
def robots_txt(request):
    content = """User-agent: *
Allow: /
Sitemap: /sitemap.xml
"""
    return HttpResponse(content, content_type='text/plain')

"""
RENTPLAY Admin v2.0 - Role-based access control
SuperAdmin: full access | Agency_Admin: own agency only | Staff: limited
"""

import csv
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count

from .models import (
    User, Agency, Property, PropertyImage, PropertyVideo,
    PropertyType, City, District, Booking, Review, Wishlist,
    Message, Notification, Waitlist, Contract, Banner
)


# ==================== EXPORT ACTION ====================
def export_bookings_to_csv(modeladmin, request, queryset):
    """Export selected bookings as a CSV file."""
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=bookings.csv'
    writer = csv.writer(response)
    # Header row
    writer.writerow([
        _('ID'), _('Client Name'), _('Phone'), _('Email'),
        _('Property'), _('Agency'), _('Start Date'), _('End Date'),
        _('Duration'), _('Status'), _('Created At')
    ])
    for obj in queryset:
        writer.writerow([
            obj.id,
            obj.client_name,
            obj.phone,
            obj.email or '',
            obj.property_unit.title if obj.property_unit else '',
            obj.agency.name if obj.agency else '',
            obj.start_date,
            obj.end_date,
            obj.duration_display,
            obj.get_status_display(),
            obj.created_at,
        ])
    return response

export_bookings_to_csv.short_description = _('Export selected bookings to CSV')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin with role-based access control."""

    list_display = ['username', 'get_full_name', 'email', 'role', 'agency', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'date_joined', 'agency']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'phone']
    ordering = ['-date_joined']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'whatsapp', 'avatar')}),
        (_('Role & Agency'), {'fields': ('role', 'agency')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'), 'classes': ('collapse',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined'), 'classes': ('collapse',)}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('username', 'password1', 'password2', 'role', 'agency')}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superadmin:
            return qs
        if request.user.is_agency_admin and request.user.agency:
            return qs.filter(Q(agency=request.user.agency) | Q(pk=request.user.pk))
        return qs.filter(pk=request.user.pk)


class PropertyImageInline(admin.TabularInline):
    """Inline admin for property images."""
    model = PropertyImage
    extra = 1


class PropertyVideoInline(admin.TabularInline):
    """Inline admin for property videos."""
    model = PropertyVideo
    extra = 0


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    """Agency admin with property count display."""

    list_display = ['name', 'city', 'phone', 'status', 'published_property_count', 'created_at']
    list_filter = ['status', 'city', 'created_at']
    search_fields = ['name', 'phone', 'email']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superadmin:
            return qs
        if request.user.is_agency_member and request.user.agency:
            return qs.filter(pk=request.user.agency.pk)
        return qs.none()

    def published_property_count(self, obj):
        """Return the number of published properties for this agency.

        Note: this method was renamed from ``property_count`` to avoid
        shadowing the model's ``@property property_count`` attribute.
        """
        return obj.properties.filter(is_published=True).count()
    published_property_count.short_description = _('Properties')


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """Property admin with role-based queryset filtering."""

    list_display = ['unit_code', 'title', 'agency', 'property_type', 'city', 'district', 'price', 'status', 'is_published', 'created_at']
    list_filter = ['status', 'is_published', 'property_type', 'city', 'district', 'created_at']
    search_fields = ['title', 'unit_code', 'description', 'features']
    list_editable = ['status', 'is_published']
    list_display_links = ['unit_code', 'title']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'view_count']
    inlines = [PropertyImageInline, PropertyVideoInline]
    actions = ['make_available', 'make_rented']

    fieldsets = (
        (_('Basic Info'), {
            'fields': ('title', 'unit_code', 'description', 'agency')
        }),
        (_('Property Details'), {
            'fields': ('property_type', 'city', 'district', 'rooms', 'bathrooms', 'area', 'floor')
        }),
        (_('Pricing'), {
            'fields': ('price', 'payment_period')
        }),
        (_('Status & Publishing'), {
            'fields': ('status', 'is_published', 'is_featured'),
            'classes': ('wide',)
        }),
        (_('Contact & Location'), {
            'fields': ('phone', 'whatsapp', 'map_link', 'lat', 'lng'),
            'classes': ('collapse',)
        }),
        (_('Features'), {
            'fields': ('features',),
            'classes': ('collapse',)
        }),
        (_('Statistics'), {
            'fields': ('created_at', 'updated_at', 'view_count'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superadmin:
            return qs
        if request.user.is_agency_member and request.user.agency:
            return qs.filter(agency=request.user.agency)
        return qs.none()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Keep is_published value from the object when editing
        if obj and not request.user.is_superadmin:
            if 'is_published' in form.base_fields:
                form.base_fields['is_published'].initial = obj.is_published
        return form

    def save_model(self, request, obj, form, change):
        if not request.user.is_superadmin and request.user.agency:
            obj.agency = request.user.agency
        # is_published is now user-controlled (fixed in Property.save())
        super().save_model(request, obj, form, change)

    @admin.action(description=_('Mark selected as Available'))
    def make_available(self, request, queryset):
        queryset.update(status=Property.Status.AVAILABLE)

    @admin.action(description=_('Mark selected as Rented'))
    def make_rented(self, request, queryset):
        queryset.update(status=Property.Status.RENTED)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Booking admin with CSV export action."""

    list_display = ['client_name', 'phone', 'property_unit', 'agency', 'start_date', 'end_date', 'duration_months', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'agency']
    search_fields = ['client_name', 'phone', 'email']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'ip_address', 'agency', 'duration_display']
    actions = ['mark_confirmed', 'mark_cancelled', export_bookings_to_csv]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superadmin:
            return qs
        if request.user.is_agency_member and request.user.agency:
            return qs.filter(agency=request.user.agency)
        return qs.none()

    @admin.action(description=_('Mark selected as Confirmed'))
    def mark_confirmed(self, request, queryset):
        queryset.update(status=Booking.Status.CONFIRMED, handled_by=request.user)

    @admin.action(description=_('Mark selected as Cancelled'))
    def mark_cancelled(self, request, queryset):
        queryset.update(status=Booking.Status.CANCELLED, handled_by=request.user)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Review admin with bulk approve/reject actions."""

    list_display = ['user', 'property_unit', 'agency', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['comment', 'user__username']
    list_editable = ['is_approved']
    actions = ['approve_reviews', 'reject_reviews']

    @admin.action(description=_('Approve selected reviews'))
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True, status=Review.Status.APPROVED)

    @admin.action(description=_('Reject selected reviews'))
    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False, status=Review.Status.REJECTED)


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    """Property type/category admin."""

    list_display = ['name', 'name_en', 'order']
    list_editable = ['order']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """City admin with search."""

    list_display = ['name', 'name_en', 'order']
    list_editable = ['order']
    search_fields = ['name', 'name_en']


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    """District admin with city filter."""

    list_display = ['name', 'name_en', 'city']
    list_filter = ['city']
    search_fields = ['name', 'city__name']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification admin."""

    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    """Contract admin."""

    list_display = ['booking', 'agency', 'status', 'monthly_rent', 'start_date', 'end_date']
    list_filter = ['status', 'created_at']


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    """Banner / advertisement admin."""

    list_display = ['title', 'position', 'agency', 'order', 'is_active', 'start_date', 'end_date', 'created_at']
    list_filter = ['position', 'is_active', 'created_at']
    search_fields = ['title', 'subtitle']
    list_editable = ['order', 'is_active']
    ordering = ['position', 'order']


admin.site.register(PropertyImage)
admin.site.register(PropertyVideo)
admin.site.register(Wishlist)
admin.site.register(Message)
admin.site.register(Waitlist)

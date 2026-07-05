"""
RENTPLAY Core Models v2.0
Multi-Vendor Real Estate Marketplace
Includes: User, City, District, Agency, Property, Booking, Review, Wishlist, Message, Notification, Waitlist, Contract, Banner
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils.text import slugify


# ==================== CUSTOM USER ====================
class User(AbstractUser):
    """Custom User with 4 roles."""

    class Role(models.TextChoices):
        SUPERADMIN = 'superadmin', _('Super Admin')
        AGENCY_ADMIN = 'agency_admin', _('Agency Admin')
        AGENCY_STAFF = 'agency_staff', _('Agency Staff')
        REGULAR_USER = 'regular_user', _('Regular User')

    role = models.CharField(
        _('user role'), max_length=20, choices=Role.choices, default=Role.REGULAR_USER
    )
    phone = models.CharField(
        _('phone number'), max_length=20, blank=True,
        validators=[RegexValidator(regex=r'^05\d{8}$', message=_('Enter a valid Saudi phone number starting with 05.'))]
    )
    whatsapp = models.CharField(_('WhatsApp number'), max_length=15, blank=True, help_text=_('Format: 9665XXXXXXXX'))
    avatar = models.ImageField(_('profile picture'), upload_to='avatars/', blank=True, null=True)
    agency = models.ForeignKey(
        'Agency', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_('belongs to agency'), related_name='members'
    )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_superadmin(self):
        return self.role == self.Role.SUPERADMIN or self.is_superuser

    @property
    def is_agency_admin(self):
        return self.role == self.Role.AGENCY_ADMIN

    @property
    def is_agency_staff(self):
        return self.role == self.Role.AGENCY_STAFF

    @property
    def is_agency_member(self):
        return self.is_agency_admin or self.is_agency_staff

    @property
    def is_regular_user(self):
        return self.role == self.Role.REGULAR_USER

    def can_access_admin(self):
        return self.is_superadmin or self.is_agency_admin or self.is_agency_staff

    def unread_notifications_count(self):
        return self.notifications.filter(is_read=False).count()


# ==================== CITY ====================
class City(models.Model):
    """City model for property locations."""

    name = models.CharField(_('city name'), max_length=100, unique=True)
    name_en = models.CharField(_('city name (English)'), max_length=100, blank=True)
    order = models.PositiveIntegerField(_('display order'), default=0)
    lat = models.DecimalField(_('latitude'), max_digits=10, decimal_places=7, null=True, blank=True)
    lng = models.DecimalField(_('longitude'), max_digits=10, decimal_places=7, null=True, blank=True)

    class Meta:
        verbose_name = _('city')
        verbose_name_plural = _('cities')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


# ==================== DISTRICT ====================
class District(models.Model):
    """District model linked to a city."""

    city = models.ForeignKey(
        City, on_delete=models.CASCADE, verbose_name=_('city'), related_name='districts'
    )
    name = models.CharField(_('district name'), max_length=100)
    name_en = models.CharField(_('district name (English)'), max_length=100, blank=True)
    lat = models.DecimalField(_('latitude'), max_digits=10, decimal_places=7, null=True, blank=True)
    lng = models.DecimalField(_('longitude'), max_digits=10, decimal_places=7, null=True, blank=True)

    class Meta:
        verbose_name = _('district')
        verbose_name_plural = _('districts')
        constraints = [
            models.UniqueConstraint(fields=['city', 'name'], name='unique_district_per_city')
        ]
        ordering = ['city', 'name']

    def __str__(self):
        return f"{self.name} - {self.city.name}"


# ==================== AGENCY ====================
class Agency(models.Model):
    """Real estate agency model."""

    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        PENDING = 'pending', _('Pending Approval')
        SUSPENDED = 'suspended', _('Suspended')

    name = models.CharField(_('agency name'), max_length=200, unique=True)
    slug = models.SlugField(_('URL slug'), max_length=250, unique=True)
    description = models.TextField(_('description'), blank=True)
    logo = models.ImageField(_('agency logo'), upload_to='agencies/logos/', blank=True, null=True)
    phone = models.CharField(_('phone number'), max_length=20, blank=True)
    whatsapp = models.CharField(_('WhatsApp number'), max_length=15, blank=True)
    email = models.EmailField(_('email'), blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    district = models.CharField(_('district'), max_length=100, blank=True)
    address = models.TextField(_('address'), blank=True)
    map_link = models.URLField(_('Google Maps link'), blank=True)
    lat = models.DecimalField(_('latitude'), max_digits=10, decimal_places=7, null=True, blank=True)
    lng = models.DecimalField(_('longitude'), max_digits=10, decimal_places=7, null=True, blank=True)
    admin = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_('agency admin'), related_name='managed_agency',
        limit_choices_to={'role': User.Role.AGENCY_ADMIN}
    )
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.PENDING)
    commission_rate = models.DecimalField(_('commission rate (%)'), max_digits=5, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('agency')
        verbose_name_plural = _('agencies')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or 'agency'
            slug, counter = base, 1
            while Agency.objects.filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('rentplay:agency_detail', kwargs={'agency_slug': self.slug})

    @property
    def property_count(self):
        return self.properties.filter(is_published=True).count()

    @property
    def available_count(self):
        return self.properties.filter(is_published=True, status='available').count()

    @property
    def rented_count(self):
        return self.properties.filter(is_published=True, status='rented').count()

    def average_rating(self):
        reviews = Review.objects.filter(agency=self, is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0


# ==================== PROPERTY TYPE ====================
class PropertyType(models.Model):
    """Property type/category model."""

    name = models.CharField(_('type name'), max_length=100, unique=True)
    name_en = models.CharField(_('type name (English)'), max_length=100, blank=True)
    icon = models.CharField(_('icon class'), max_length=50, blank=True, help_text=_('Font Awesome icon class'))
    order = models.PositiveIntegerField(_('display order'), default=0)

    class Meta:
        verbose_name = _('property type')
        verbose_name_plural = _('property types')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


# ==================== PROPERTY ====================
class Property(models.Model):
    """Property/unit listing model."""

    class Status(models.TextChoices):
        AVAILABLE = 'available', _('Available')
        RENTED = 'rented', _('Rented')
        MAINTENANCE = 'maintenance', _('Under Maintenance')

    class PaymentPeriod(models.TextChoices):
        MONTHLY = 'monthly', _('Monthly')
        QUARTERLY = 'quarterly', _('Every 3 Months')
        FOUR_MONTHS = 'four_months', _('Every 4 Months')
        SIX_MONTHS = 'six_months', _('Every 6 Months')
        YEARLY = 'yearly', _('Yearly')

    unit_code = models.CharField(_('unit code'), max_length=50, unique=True, help_text=_('Unique code (e.g., R001)'))
    agency = models.ForeignKey(
        Agency, on_delete=models.CASCADE, verbose_name=_('agency'), related_name='properties'
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_('created by'), related_name='created_properties'
    )
    title = models.CharField(_('property title'), max_length=300)
    description = models.TextField(_('description'), blank=True)
    property_type = models.ForeignKey(
        PropertyType, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_('property type'), related_name='properties'
    )
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_('city'), related_name='properties'
    )
    district = models.ForeignKey(
        District, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_('district'), related_name='properties'
    )
    rooms = models.PositiveIntegerField(_('number of rooms'), default=1, validators=[MinValueValidator(0)])
    bathrooms = models.PositiveIntegerField(_('number of bathrooms'), default=1, validators=[MinValueValidator(0)])
    area = models.PositiveIntegerField(_('area (sqm)'), null=True, blank=True)
    floor = models.IntegerField(_('floor number'), null=True, blank=True)
    price = models.DecimalField(_('monthly rent (SAR)'), max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    payment_period = models.CharField(_('payment period'), max_length=20, choices=PaymentPeriod.choices, default=PaymentPeriod.MONTHLY)
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    rent_end_date = models.DateField(_('rent end date'), null=True, blank=True)
    phone = models.CharField(_('contact phone'), max_length=20, blank=True)
    whatsapp = models.CharField(_('WhatsApp number'), max_length=15, blank=True)
    map_link = models.URLField(_('Google Maps link'), blank=True)
    lat = models.DecimalField(_('latitude'), max_digits=10, decimal_places=7, null=True, blank=True)
    lng = models.DecimalField(_('longitude'), max_digits=10, decimal_places=7, null=True, blank=True)
    features = models.TextField(_('features'), blank=True, help_text=_('Comma-separated features'))
    is_published = models.BooleanField(_('published'), default=True)
    is_featured = models.BooleanField(_('featured'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    view_count = models.PositiveIntegerField(_('view count'), default=0)

    class Meta:
        verbose_name = _('property')
        verbose_name_plural = _('properties')
        ordering = ['-is_featured', 'status', '-created_at']
        get_latest_by = ['created_at']
        constraints = [
            models.UniqueConstraint(fields=['agency', 'title'], name='unique_property_title_per_agency')
        ]

    def __str__(self):
        return f"{self.title} ({self.unit_code})"

    def get_absolute_url(self):
        return reverse('rentplay:property_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        """Save property without forcing is_published — let users control it."""
        super().save(*args, **kwargs)

    @property
    def feature_list(self):
        if not self.features:
            return []
        return [f.strip() for f in self.features.replace('\u060c', ',').split(',') if f.strip()]

    @property
    def main_image(self):
        first = self.images.first()
        return first.image.url if first else None

    def increment_views(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def average_rating(self):
        reviews = Review.objects.filter(property_unit=self, is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0

    def review_count(self):
        return Review.objects.filter(property_unit=self, is_approved=True).count()


# ==================== PROPERTY IMAGE ====================
class PropertyImage(models.Model):
    """Property image gallery item."""

    property_unit = models.ForeignKey(
        Property, on_delete=models.CASCADE, verbose_name=_('property'), related_name='images'
    )
    image = models.ImageField(_('image'), upload_to='properties/images/%Y/%m/')
    caption = models.CharField(_('caption'), max_length=200, blank=True)
    order = models.PositiveIntegerField(_('display order'), default=0)
    uploaded_at = models.DateTimeField(_('uploaded at'), auto_now_add=True)

    class Meta:
        verbose_name = _('property image')
        verbose_name_plural = _('property images')
        ordering = ['order', 'uploaded_at']


# ==================== PROPERTY VIDEO ====================
class PropertyVideo(models.Model):
    """Property video model."""

    property_unit = models.ForeignKey(
        Property, on_delete=models.CASCADE, verbose_name=_('property'), related_name='videos'
    )
    video = models.FileField(_('video'), upload_to='properties/videos/%Y/%m/', help_text=_('Max 10MB. MP4 format.'))
    caption = models.CharField(_('caption'), max_length=200, blank=True)
    order = models.PositiveIntegerField(_('display order'), default=0)
    uploaded_at = models.DateTimeField(_('uploaded at'), auto_now_add=True)

    class Meta:
        verbose_name = _('property video')
        verbose_name_plural = _('property videos')
        ordering = ['order', 'uploaded_at']


# ==================== BOOKING ====================
class Booking(models.Model):
    """Booking / reservation model."""

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        CONFIRMED = 'confirmed', _('Confirmed')
        CANCELLED = 'cancelled', _('Cancelled')
        COMPLETED = 'completed', _('Completed')

    property_unit = models.ForeignKey(
        Property, on_delete=models.CASCADE, verbose_name=_('property'), related_name='bookings'
    )
    agency = models.ForeignKey(
        Agency, on_delete=models.CASCADE, verbose_name=_('target agency'), related_name='bookings'
    )
    client_name = models.CharField(_('client name'), max_length=200)
    phone = models.CharField(
        _('phone number'), max_length=20,
        validators=[RegexValidator(regex=r'^05\d{8}$', message=_('Valid Saudi phone starting with 05'))]
    )
    email = models.EmailField(_('email address'), blank=True)
    start_date = models.DateField(_('check-in date'))
    end_date = models.DateField(_('check-out date'))
    duration_months = models.PositiveIntegerField(_('duration in months'), default=1)
    duration_display = models.CharField(_('duration display'), max_length=100, blank=True)
    status = models.CharField(_('booking status'), max_length=20, choices=Status.choices, default=Status.PENDING)
    internal_notes = models.TextField(_('internal notes'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    handled_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_('handled by'), related_name='handled_bookings'
    )
    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)

    class Meta:
        verbose_name = _('booking')
        verbose_name_plural = _('bookings')
        ordering = ['-created_at']
        get_latest_by = ['created_at']

    def __str__(self):
        return f"{self.client_name} - {self.property_unit.title} ({self.start_date} to {self.end_date})"

    def save(self, *args, **kwargs):
        """Auto-fill agency from property and calculate duration display."""
        if self.property_unit and not self.agency_id:
            self.agency = self.property_unit.agency
        if self.start_date and self.end_date:
            self.duration_display = self.calculate_duration_display()
        super().save(*args, **kwargs)

    def calculate_duration_display(self):
        """Calculate a human-readable duration string between start_date and end_date."""
        if not self.start_date or not self.end_date:
            return ""
        try:
            from dateutil.relativedelta import relativedelta
            rd = relativedelta(self.end_date, self.start_date)
        except Exception:
            # Fallback: manual calculation if dateutil is unavailable
            from datetime import date
            d1 = date(self.start_date.year, self.start_date.month, self.start_date.day)
            d2 = date(self.end_date.year, self.end_date.month, self.end_date.day)
            if d2 < d1:
                return ""
            years = d2.year - d1.year
            months = d2.month - d1.month
            days = d2.day - d1.day
            if days < 0:
                months -= 1
                # Approximate days in previous month
                prev_month = (d2.replace(day=1) - __import__('datetime').timedelta(days=1)).day
                days += prev_month
            if months < 0:
                years -= 1
                months += 12
            rd = type('RD', (), {'years': years, 'months': months, 'days': days})()

        parts = []
        if rd.years > 0:
            parts.append(f"{rd.years} {_('year')}{'s' if rd.years > 1 else ''}")
        if rd.months > 0:
            parts.append(f"{rd.months} {_('month')}{'s' if rd.months > 1 else ''}")
        if rd.days > 0:
            parts.append(f"{rd.days} {_('day')}{'s' if rd.days > 1 else ''}")
        return ", ".join(parts) if parts else _("0 days")

    @property
    def status_css_class(self):
        classes = {
            'pending': 'badge-warning',
            'confirmed': 'badge-success',
            'cancelled': 'badge-danger',
            'completed': 'badge-info',
        }
        return classes.get(self.status, 'badge-info')


# ==================== REVIEW (NEW) ====================
class Review(models.Model):
    """User review for a property or agency."""

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending Approval')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_('user'), related_name='reviews'
    )
    property_unit = models.ForeignKey(
        Property, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name=_('property'), related_name='reviews'
    )
    agency = models.ForeignKey(
        Agency, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name=_('agency'), related_name='reviews'
    )
    rating = models.PositiveIntegerField(
        _('rating'), validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_('Rate from 1 to 5 stars')
    )
    comment = models.TextField(_('comment'), blank=True)
    is_approved = models.BooleanField(_('approved'), default=False)
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('review')
        verbose_name_plural = _('reviews')
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'property_unit'], name='unique_review_per_user_property')
        ]

    def __str__(self):
        target = self.property_unit or self.agency
        return f"{self.user.username} - {target} - {self.rating}\u2605"


# ==================== WISHLIST (NEW) ====================
class Wishlist(models.Model):
    """User wishlist / favorites for properties."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_('user'), related_name='wishlist'
    )
    property_unit = models.ForeignKey(
        Property, on_delete=models.CASCADE, verbose_name=_('property'), related_name='wishlisted_by'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('wishlist item')
        verbose_name_plural = _('wishlist items')
        constraints = [
            models.UniqueConstraint(fields=['user', 'property_unit'], name='unique_wishlist_per_user_property')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} \u2764 {self.property_unit.title}"


# ==================== MESSAGE / CHAT (NEW) ====================
class Message(models.Model):
    """Chat message between users."""

    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_('sender'), related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_('receiver'), related_name='received_messages'
    )
    property_unit = models.ForeignKey(
        Property, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name=_('property'), related_name='messages'
    )
    content = models.TextField(_('message content'))
    is_read = models.BooleanField(_('read'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.username} \u2192 {self.receiver.username}: {self.content[:30]}..."


# ==================== NOTIFICATION (NEW) ====================
class Notification(models.Model):
    """User notification model."""

    class Type(models.TextChoices):
        BOOKING = 'booking', _('New Booking')
        MESSAGE = 'message', _('New Message')
        REVIEW = 'review', _('New Review')
        STATUS = 'status', _('Status Update')
        SYSTEM = 'system', _('System')

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_('user'), related_name='notifications'
    )
    notification_type = models.CharField(_('type'), max_length=20, choices=Type.choices, default=Type.SYSTEM)
    title = models.CharField(_('title'), max_length=200)
    message = models.TextField(_('message'))
    link = models.URLField(_('link'), blank=True)
    is_read = models.BooleanField(_('read'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"


# ==================== WAITLIST / ALERT (NEW) ====================
class Waitlist(models.Model):
    """Waitlist for users who want to be notified when a property becomes available."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_('user'), related_name='waitlists'
    )
    property_unit = models.ForeignKey(
        Property, on_delete=models.CASCADE, verbose_name=_('property'), related_name='waitlisted_by'
    )
    email = models.EmailField(_('email'))
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    notified = models.BooleanField(_('notified'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('waitlist entry')
        verbose_name_plural = _('waitlist entries')
        constraints = [
            models.UniqueConstraint(fields=['user', 'property_unit'], name='unique_waitlist_per_user_property')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} waiting for {self.property_unit.title}"


# ==================== BANNER / AD SLIDER ====================
class Banner(models.Model):
    """Banner / advertisement slider model."""

    class Position(models.TextChoices):
        HERO = 'hero', _('Hero Slider (Top)')
        SIDEBAR = 'sidebar', _('Sidebar')
        FOOTER = 'footer', _('Footer')

    title = models.CharField(_('ad title'), max_length=200)
    subtitle = models.CharField(_('subtitle'), max_length=300, blank=True)
    image = models.ImageField(_('banner image'), upload_to='banners/%Y/%m/')
    link = models.URLField(_('link URL'), blank=True, help_text=_('Where users go when clicking the banner'))
    agency = models.ForeignKey(
        Agency, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_('agency'), related_name='banners'
    )
    position = models.CharField(_('position'), max_length=20, choices=Position.choices, default=Position.HERO)
    order = models.PositiveIntegerField(_('display order'), default=0)
    is_active = models.BooleanField(_('active'), default=True)
    start_date = models.DateField(_('start date'), null=True, blank=True)
    end_date = models.DateField(_('end date'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('banner')
        verbose_name_plural = _('banners')
        ordering = ['position', 'order', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_position_display()})"


# ==================== CONTRACT (NEW) ====================
class Contract(models.Model):
    """Rental contract linked to a booking."""

    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        SENT = 'sent', _('Sent')
        SIGNED = 'signed', _('Signed')
        ACTIVE = 'active', _('Active')
        EXPIRED = 'expired', _('Expired')
        CANCELLED = 'cancelled', _('Cancelled')

    booking = models.OneToOneField(
        Booking, on_delete=models.CASCADE, verbose_name=_('booking'), related_name='contract'
    )
    agency = models.ForeignKey(
        Agency, on_delete=models.CASCADE, verbose_name=_('agency'), related_name='contracts'
    )
    document = models.FileField(_('contract document'), upload_to='contracts/%Y/%m/', blank=True, null=True)
    monthly_rent = models.DecimalField(_('monthly rent'), max_digits=12, decimal_places=2)
    deposit_amount = models.DecimalField(_('deposit amount'), max_digits=12, decimal_places=2, default=0)
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    status = models.CharField(_('status'), max_length=20, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(_('notes'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('contract')
        verbose_name_plural = _('contracts')
        ordering = ['-created_at']

    def __str__(self):
        return f"Contract #{self.id} - {self.booking.client_name}"

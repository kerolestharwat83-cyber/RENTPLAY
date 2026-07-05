"""
RENTPLAY Forms v2.0
Includes authentication, property management, booking, reviews, messaging,
waitlist, and advanced search forms.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from .models import (
    User, Property, Booking, City, District, PropertyType, Agency,
    Review, Message, Waitlist
)


# ==================== AUTH FORMS ====================
class LoginForm(AuthenticationForm):
    """Custom login form with styled widgets."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Username')}),
        label=_('Username')
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': _('Password')}),
        label=_('Password')
    )


class UserRegistrationForm(UserCreationForm):
    """User registration form with email uniqueness validation."""

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('First Name')}),
        label=_('First Name'), required=True
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Last Name')}),
        label=_('Last Name'), required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': _('Email')}),
        label=_('Email'), required=True
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('05XXXXXXXX')}),
        label=_('Phone'),
        validators=[RegexValidator(regex=r'^05\d{8}$', message=_('Valid Saudi phone starting with 05'))]
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['username', 'password1', 'password2']:
            self.fields[field].widget.attrs.update({'class': 'form-input'})

    def clean_username(self):
        username = self.cleaned_data.get('username', '').lower().strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(_('This username is already taken. Please choose another one.'))
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_('An account with this email already exists. Please use a different email or log in.'))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.REGULAR_USER
        if commit:
            user.save()
        return user


# ==================== PROPERTY FILTER FORM ====================
class PropertyFilterForm(forms.Form):
    """Basic property filter form for list views."""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Search by name or code...')}),
        label=_('Search')
    )
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        required=False, empty_label=_('All Cities'),
        widget=forms.Select(attrs={'class': 'form-input', 'id': 'id_city'}),
        label=_('City')
    )
    district = forms.ModelChoiceField(
        queryset=District.objects.none(),
        required=False, empty_label=_('All Districts'),
        widget=forms.Select(attrs={'class': 'form-input', 'id': 'id_district'}),
        label=_('District')
    )
    property_type = forms.ModelChoiceField(
        queryset=PropertyType.objects.all(),
        required=False, empty_label=_('All Types'),
        widget=forms.Select(attrs={'class': 'form-input'}),
        label=_('Property Type')
    )
    max_price = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': _('e.g., 10000'), 'min': 0}),
        label=_('Max Price (SAR)')
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', _('All Status'))] + list(Property.Status.choices),
        widget=forms.Select(attrs={'class': 'form-input'}),
        label=_('Status')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.data.get('city'):
            try:
                city_id = int(self.data.get('city'))
                self.fields['district'].queryset = District.objects.filter(city_id=city_id)
            except (ValueError, TypeError):
                pass
        elif self.initial.get('city'):
            try:
                city_id = int(self.initial.get('city'))
                self.fields['district'].queryset = District.objects.filter(city_id=city_id)
            except (ValueError, TypeError):
                pass


# ==================== PROPERTY SEARCH FORM (Advanced) ====================
class PropertySearchForm(forms.Form):
    """Advanced property search form with price and rooms range filters."""

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Search by title, code, or description...')}),
        label=_('Keywords')
    )
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        required=False, empty_label=_('All Cities'),
        widget=forms.Select(attrs={'class': 'form-input', 'id': 'search_city'}),
        label=_('City')
    )
    district = forms.ModelChoiceField(
        queryset=District.objects.none(),
        required=False, empty_label=_('All Districts'),
        widget=forms.Select(attrs={'class': 'form-input', 'id': 'search_district'}),
        label=_('District')
    )
    property_type = forms.ModelChoiceField(
        queryset=PropertyType.objects.all(),
        required=False, empty_label=_('All Types'),
        widget=forms.Select(attrs={'class': 'form-input'}),
        label=_('Property Type')
    )
    min_price = forms.DecimalField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': _('Min'), 'min': 0}),
        label=_('Min Price (SAR)')
    )
    max_price = forms.DecimalField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': _('Max'), 'min': 0}),
        label=_('Max Price (SAR)')
    )
    min_rooms = forms.IntegerField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': _('Min rooms'), 'min': 0}),
        label=_('Min Rooms')
    )
    max_rooms = forms.IntegerField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': _('Max rooms'), 'min': 0}),
        label=_('Max Rooms')
    )
    min_area = forms.IntegerField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': _('Min sqm'), 'min': 0}),
        label=_('Min Area (sqm)')
    )
    max_area = forms.IntegerField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': _('Max sqm'), 'min': 0}),
        label=_('Max Area (sqm)')
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', _('All Status'))] + list(Property.Status.choices),
        widget=forms.Select(attrs={'class': 'form-input'}),
        label=_('Status')
    )
    is_featured = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(),
        label=_('Featured Only')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.data.get('city'):
            try:
                city_id = int(self.data.get('city'))
                self.fields['district'].queryset = District.objects.filter(city_id=city_id)
            except (ValueError, TypeError):
                pass
        elif self.initial.get('city'):
            try:
                city_id = int(self.initial.get('city'))
                self.fields['district'].queryset = District.objects.filter(city_id=city_id)
            except (ValueError, TypeError):
                pass

    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        if min_price and max_price and min_price > max_price:
            raise forms.ValidationError(_('Minimum price cannot be greater than maximum price.'))
        min_rooms = cleaned_data.get('min_rooms')
        max_rooms = cleaned_data.get('max_rooms')
        if min_rooms and max_rooms and min_rooms > max_rooms:
            raise forms.ValidationError(_('Minimum rooms cannot be greater than maximum rooms.'))
        min_area = cleaned_data.get('min_area')
        max_area = cleaned_data.get('max_area')
        if min_area and max_area and min_area > max_area:
            raise forms.ValidationError(_('Minimum area cannot be greater than maximum area.'))
        return cleaned_data


# ==================== PROPERTY FORM ====================
class PropertyForm(forms.ModelForm):
    """Property creation/editing form with video upload support."""

    features_text = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('AC, Heater, Internet, Security, Garage')}),
        label=_('Features'),
        help_text=_('Separate features with commas')
    )
    lat = forms.DecimalField(
        required=False, widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': _('24.7136')}),
        label=_('Latitude'), max_digits=10, decimal_places=7
    )
    lng = forms.DecimalField(
        required=False, widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': _('46.6753')}),
        label=_('Longitude'), max_digits=10, decimal_places=7
    )
    videos = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-input', 'multiple': True, 'accept': 'video/mp4,video/webm'}),
        label=_('Upload Videos'),
        help_text=_('Upload one or more videos (MP4/WebM, max 10MB each)')
    )

    class Meta:
        model = Property
        fields = [
            'unit_code', 'title', 'description', 'property_type',
            'city', 'district', 'rooms', 'bathrooms', 'area', 'floor',
            'price', 'payment_period', 'status', 'rent_end_date',
            'phone', 'whatsapp', 'map_link', 'features_text', 'lat', 'lng',
            'is_published', 'is_featured', 'videos'
        ]
        widgets = {
            'unit_code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'R001'}),
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'property_type': forms.Select(attrs={'class': 'form-input'}),
            'city': forms.Select(attrs={'class': 'form-input', 'id': 'prop_city'}),
            'district': forms.Select(attrs={'class': 'form-input', 'id': 'prop_district'}),
            'rooms': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'area': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'floor': forms.NumberInput(attrs={'class': 'form-input'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'payment_period': forms.Select(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'rent_end_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '05XXXXXXXX'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '9665XXXXXXXX'}),
            'map_link': forms.URLInput(attrs={'class': 'form-input'}),
            'is_published': forms.CheckboxInput(),
            'is_featured': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['features_text'].initial = self.instance.features
            self.fields['lat'].initial = self.instance.lat
            self.fields['lng'].initial = self.instance.lng
        if self.instance and self.instance.city:
            self.fields['district'].queryset = District.objects.filter(city=self.instance.city)
        elif self.data.get('city'):
            try:
                self.fields['district'].queryset = District.objects.filter(city_id=int(self.data.get('city')))
            except (ValueError, TypeError):
                pass
        else:
            self.fields['district'].queryset = District.objects.none()

    def clean_unit_code(self):
        unit_code = self.cleaned_data.get('unit_code', '').upper().strip()
        qs = Property.objects.filter(unit_code=unit_code)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_('This unit code is already in use.'))
        return unit_code

    def clean_title(self):
        """Case-insensitive duplicate title check per agency."""
        title = self.cleaned_data.get('title', '').strip()
        # Get agency from instance (since agency is not in form fields, it's set in save())
        agency = None
        if self.instance and self.instance.pk:
            agency = self.instance.agency
        # Fallback: try to get from the user if creating a new property
        if not agency and self.user and hasattr(self.user, 'agency') and self.user.agency:
            agency = self.user.agency

        if agency and title:
            qs = Property.objects.filter(agency=agency, title__iexact=title)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    _('This agency already has a property with this title. Please use a different title.')
                )
        return title

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.features = self.cleaned_data.get('features_text', '')
        instance.lat = self.cleaned_data.get('lat')
        instance.lng = self.cleaned_data.get('lng')
        if self.user and not instance.created_by:
            instance.created_by = self.user
        if commit:
            instance.save()
            self.save_m2m()
        return instance


# ==================== PROPERTY STATUS FORM (Quick Toggle) ====================
class PropertyStatusForm(forms.ModelForm):
    """Quick status toggle form for properties."""

    class Meta:
        model = Property
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-input'}),
        }


# ==================== BOOKING FORM ====================
class BookingForm(forms.ModelForm):
    """Booking form with honeypot spam protection and agency auto-assignment."""

    website = forms.CharField(required=False, widget=forms.HiddenInput)
    agency = forms.ModelChoiceField(
        queryset=Agency.objects.all(),
        required=False,
        widget=forms.HiddenInput,
    )
    number_of_months = forms.IntegerField(
        required=False, min_value=1, max_value=120,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'id': 'number_of_months', 'placeholder': _('e.g., 6'), 'min': 1}),
        label=_('Number of Months'),
        help_text=_('Enter months to auto-calculate the end date')
    )
    duration_years = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input readonly-field', 'id': 'duration_years', 'readonly': 'readonly', 'placeholder': '0'}),
        label=_('Years')
    )
    duration_months_display = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input readonly-field', 'id': 'duration_months_display', 'readonly': 'readonly', 'placeholder': '0'}),
        label=_('Months')
    )
    duration_days = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input readonly-field', 'id': 'duration_days', 'readonly': 'readonly', 'placeholder': '0'}),
        label=_('Days')
    )

    class Meta:
        model = Booking
        fields = ['client_name', 'phone', 'email', 'start_date', 'end_date', 'agency', 'website']
        widgets = {
            'client_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Full Name'), 'required': True}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('05XXXXXXXX'), 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': _('Email (optional)')}),
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date', 'id': 'checkin_date', 'required': True}),
            'end_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date', 'id': 'checkout_date', 'required': True}),
        }

    def __init__(self, *args, **kwargs):
        self.property_obj = kwargs.pop('property_obj', None)
        super().__init__(*args, **kwargs)

    def clean_website(self):
        """Honeypot field: if filled, reject submission as spam."""
        if self.cleaned_data.get('website'):
            raise forms.ValidationError(_('Invalid submission.'))
        return ''

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone and not phone.startswith('05'):
            raise forms.ValidationError(_('Phone number must start with 05.'))
        return phone

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date:
            if end_date <= start_date:
                raise forms.ValidationError(_('Check-out date must be after check-in date.'))
        return cleaned_data

    def save(self, commit=True):
        booking = super().save(commit=False)
        if self.property_obj:
            booking.property_unit = self.property_obj
            booking.agency = self.property_obj.agency
        if commit:
            booking.save()
        return booking


# ==================== PROFILE FORM ====================
class UserProfileForm(forms.ModelForm):
    """User profile editing form."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'whatsapp', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '05XXXXXXXX'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '9665XXXXXXXX'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-input'}),
        }


# ==================== REVIEW FORM (NEW) ====================
class ReviewForm(forms.ModelForm):
    """Property/agency review form."""

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': _('Write your review...')}),
        }
        labels = {
            'rating': _('Rating (1-5 stars)'),
            'comment': _('Your Review'),
        }


# ==================== MESSAGE FORM (NEW) ====================
class MessageForm(forms.ModelForm):
    """Chat message form."""

    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': _('Type your message...')}),
        }
        labels = {
            'content': _('Message'),
        }


# ==================== WAITLIST FORM (NEW) ====================
class WaitlistForm(forms.ModelForm):
    """Waitlist/join notification form."""

    class Meta:
        model = Waitlist
        fields = ['email', 'phone']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': _('your@email.com')}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('05XXXXXXXX')}),
        }
        labels = {
            'email': _('Email'),
            'phone': _('Phone (optional)'),
        }

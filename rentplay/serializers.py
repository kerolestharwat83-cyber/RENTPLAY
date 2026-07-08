"""
RENTPLAY API Serializers v2.0
DRF serializers for the real estate marketplace API.
"""

from rest_framework import serializers
from .models import (
    User, Agency, Property, PropertyImage, PropertyVideo,
    PropertyType, City, District, Booking, Review,
    Wishlist, Message, Notification
)


class CitySerializer(serializers.ModelSerializer):
    """Serializer for City model."""

    class Meta:
        model = City
        fields = ['id', 'name', 'name_en', 'order']


class DistrictSerializer(serializers.ModelSerializer):
    """Serializer for District model with nested city."""

    city = CitySerializer(read_only=True)

    class Meta:
        model = District
        fields = ['id', 'name', 'name_en', 'city']


class PropertyTypeSerializer(serializers.ModelSerializer):
    """Serializer for PropertyType model."""

    class Meta:
        model = PropertyType
        fields = ['id', 'name', 'name_en', 'icon']


class AgencySerializer(serializers.ModelSerializer):
    """Serializer for Agency model — used as nested object in property serializers."""

    class Meta:
        model = Agency
        fields = ['id', 'name', 'slug', 'description', 'logo', 'phone', 'city', 'status']


class PropertyImageSerializer(serializers.ModelSerializer):
    """Serializer for PropertyImage model."""

    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'caption', 'order']


class PropertyVideoSerializer(serializers.ModelSerializer):
    """Serializer for PropertyVideo model."""

    class Meta:
        model = PropertyVideo
        fields = ['id', 'video', 'caption', 'order']


class PropertyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for property list views."""

    agency = AgencySerializer(read_only=True)
    property_type = PropertyTypeSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    main_image = serializers.CharField(read_only=True)
    feature_list = serializers.ListField(read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'unit_code', 'title', 'agency', 'property_type',
            'city', 'district', 'rooms', 'bathrooms', 'area', 'floor',
            'price', 'payment_period', 'status', 'main_image', 'feature_list',
            'is_featured', 'created_at', 'view_count'
        ]


class PropertyDetailSerializer(serializers.ModelSerializer):
    """Full serializer for property detail views with nested images and videos."""

    agency = AgencySerializer(read_only=True)
    property_type = PropertyTypeSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    videos = PropertyVideoSerializer(many=True, read_only=True)
    main_image = serializers.CharField(read_only=True)
    feature_list = serializers.ListField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Property
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model with user name."""

    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'user_name', 'rating', 'comment', 'is_approved', 'created_at']


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model with read-only status and duration."""

    property_title = serializers.CharField(source='property_unit.title', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'property_unit', 'property_title', 'client_name',
            'phone', 'email', 'start_date', 'end_date', 'status',
            'duration_display', 'created_at'
        ]
        read_only_fields = ['status', 'duration_display']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model with sender name."""

    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_name', 'receiver', 'content', 'is_read', 'created_at']

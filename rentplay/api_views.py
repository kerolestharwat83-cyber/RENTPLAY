"""
RENTPLAY REST API v2.0
Django REST Framework API endpoints
"""

from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Property, Agency, PropertyType, City, District, Booking, Review
from .serializers import (
    PropertyListSerializer, PropertyDetailSerializer,
    AgencySerializer, PropertyTypeSerializer, CitySerializer,
    BookingSerializer, ReviewSerializer
)


class PropertyListAPI(generics.ListAPIView):
    """List all published properties with filtering"""
    serializer_class = PropertyListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['price', 'created_at', 'view_count', 'title']
    search_fields = ['title', 'description', 'features']

    def get_queryset(self):
        queryset = Property.objects.filter(is_published=True).select_related(
            'agency', 'property_type', 'city', 'district'
        ).prefetch_related('images', 'videos')

        # City filter
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__id=city)

        # District filter
        district = self.request.query_params.get('district')
        if district:
            queryset = queryset.filter(district__id=district)

        # Property type filter
        property_type = self.request.query_params.get('property_type')
        if property_type:
            queryset = queryset.filter(property_type__id=property_type)

        # Status filter
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Rooms filter
        rooms = self.request.query_params.get('rooms')
        if rooms:
            queryset = queryset.filter(rooms=rooms)

        # Price range filter
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset


class PropertyDetailAPI(generics.RetrieveAPIView):
    """Get single property details"""
    queryset = Property.objects.filter(is_published=True).select_related(
        'agency', 'property_type', 'city', 'district'
    ).prefetch_related('images', 'videos', 'reviews')
    serializer_class = PropertyDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'pk'


class AgencyListAPI(generics.ListAPIView):
    """List all active agencies"""
    queryset = Agency.objects.filter(status=Agency.Status.ACTIVE)
    serializer_class = AgencySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class AgencyDetailAPI(generics.RetrieveAPIView):
    """Get single agency details"""
    queryset = Agency.objects.filter(status=Agency.Status.ACTIVE)
    serializer_class = AgencySerializer
    lookup_field = 'slug'


class PropertyTypeListAPI(generics.ListAPIView):
    """List all property types"""
    queryset = PropertyType.objects.all()
    serializer_class = PropertyTypeSerializer


class CityListAPI(generics.ListAPIView):
    """List all cities"""
    queryset = City.objects.all()
    serializer_class = CitySerializer


@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def create_booking_api(request):
    """Create a new booking via API"""
    serializer = BookingSerializer(data=request.data)
    if serializer.is_valid():
        booking = serializer.save()
        return Response({
            'success': True,
            'message': 'Booking created successfully',
            'booking': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def property_reviews_api(request, property_pk):
    """Get reviews for a property"""
    reviews = Review.objects.filter(
        property_unit_id=property_pk, is_approved=True
    ).select_related('user')
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)

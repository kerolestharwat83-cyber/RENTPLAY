"""
RENTPLAY App URLs v2.0
"""

from django.urls import path
from . import views, api_views

app_name = 'rentplay'

urlpatterns = [
    # Landing Page
    path('', views.index, name='index'),

    # Agency Pages
    path('agencies/', views.agency_list, name='agency_list'),
    path('agencies/<slug:agency_slug>/', views.agency_detail, name='agency_detail'),

    # Property Detail & Booking
    path('property/<int:pk>/', views.property_detail, name='property_detail'),
    path('property/<int:pk>/share/', views.property_share, name='property_share'),
    path('property/<int:property_pk>/book/', views.submit_booking, name='submit_booking'),
    path('property/<int:property_pk>/review/', views.review_create, name='review_create'),
    path('property/<int:property_pk>/waitlist/', views.waitlist_join, name='waitlist_join'),
    path('property/<int:property_pk>/wishlist/', views.wishlist_toggle, name='wishlist_toggle'),

    # Compare
    path('compare/', views.property_compare, name='property_compare'),
    path('compare/add/<int:property_pk>/', views.property_compare_add, name='property_compare_add'),
    path('compare/remove/<int:property_pk>/', views.property_compare_remove, name='property_compare_remove'),

    # Map Search
    path('map-search/', views.map_search, name='map_search'),

    # AJAX
    path('ajax/districts/', views.get_districts, name='get_districts'),

    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),

    # Profile & Wishlist
    path('profile/', views.profile, name='profile'),
    path('wishlist/', views.wishlist_list, name='wishlist'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/properties/', views.dashboard_properties, name='dashboard_properties'),
    path('dashboard/properties/create/', views.property_create, name='property_create'),
    path('dashboard/properties/<int:pk>/edit/', views.property_edit, name='property_edit'),
    path('dashboard/properties/<int:pk>/delete/', views.property_delete, name='property_delete'),
    path('dashboard/properties/<int:pk>/toggle-status/', views.property_toggle_status, name='property_toggle_status'),
    path('dashboard/images/<int:image_pk>/delete/', views.delete_property_image, name='delete_property_image'),
    path('dashboard/videos/<int:video_pk>/delete/', views.delete_property_video, name='delete_property_video'),
    path('dashboard/bookings/', views.dashboard_bookings, name='dashboard_bookings'),
    path('dashboard/bookings/<int:pk>/update-status/', views.booking_update_status, name='booking_update_status'),

    # Messages
    path('messages/', views.message_list, name='message_list'),
    path('messages/<int:user_id>/', views.message_conversation, name='message_conversation'),
    path('messages/<int:user_id>/send/', views.message_send, name='message_send'),

    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:pk>/mark-read/', views.notification_mark_read, name='notification_mark_read'),

    # Language
    path('set-language/', views.set_language, name='set_language'),

    # SEO
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),

    # API v2.0
    path('api/properties/', api_views.PropertyListAPI.as_view(), name='api_properties'),
    path('api/properties/<int:pk>/', api_views.PropertyDetailAPI.as_view(), name='api_property_detail'),
    path('api/properties/<int:property_pk>/reviews/', api_views.property_reviews_api, name='api_property_reviews'),
    path('api/agencies/', api_views.AgencyListAPI.as_view(), name='api_agencies'),
    path('api/agencies/<slug:slug>/', api_views.AgencyDetailAPI.as_view(), name='api_agency_detail'),
    path('api/types/', api_views.PropertyTypeListAPI.as_view(), name='api_types'),
    path('api/cities/', api_views.CityListAPI.as_view(), name='api_cities'),
    path('api/bookings/', api_views.create_booking_api, name='api_booking'),
]

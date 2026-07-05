"""RENTPLAY Demo Data"""
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db import transaction
from rentplay.models import Agency, Property, PropertyType, City, District, Booking

User = get_user_model()

class Command(BaseCommand):
    help = _('Initialize RENTPLAY with demo data')
    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help=_('Delete existing data before creating demo data.'))
    @transaction.atomic
    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING(_('Deleting existing data...')))
            Booking.objects.all().delete(); Property.objects.all().delete(); Agency.objects.all().delete()
            District.objects.all().delete(); City.objects.all().delete(); PropertyType.objects.all().delete()
            User.objects.filter(username='admin').delete()
        self.stdout.write(self.style.HTTP_INFO(_('Creating demo data...')))
        cities_data = [
            {'name': 'الرياض', 'name_en': 'Riyadh', 'order': 1},
            {'name': 'مكة المكرمة', 'name_en': 'Makkah', 'order': 2},
            {'name': 'جدة', 'name_en': 'Jeddah', 'order': 3},
            {'name': 'الدمام', 'name_en': 'Dammam', 'order': 4},
            {'name': 'المدينة المنورة', 'name_en': 'Madinah', 'order': 5},
        ]
        cities = {}
        for data in cities_data:
            city, created = City.objects.get_or_create(name=data['name'], defaults=data)
            cities[data['name']] = city
            if created: self.stdout.write(f"  Created city: {city.name}")
        districts_map = {
            'الرياض': ['الملز', 'العزيزية', 'النزهة', 'الروضة', 'السويدي', 'العليا', 'النخيل'],
            'مكة المكرمة': ['العزيزية', 'الشوقية', 'النزهة', 'الزاهر', 'الشرائع'],
            'جدة': ['الروضة', 'الصفا', 'البوادي', 'الفيصلية', 'الخالدية'],
            'الدمام': ['الروضة', 'النزهة', 'العدامة', 'الجلوية'],
            'المدينة المنورة': ['العزيزية', 'النزهة', 'الروضة', 'العوالي'],
        }
        for city_name, district_list in districts_map.items():
            city = cities[city_name]
            for district_name in district_list:
                district, created = District.objects.get_or_create(city=city, name=district_name)
                if created: self.stdout.write(f"  Created district: {district_name} - {city_name}")
        types_data = [
            {'name': 'شقة', 'name_en': 'Apartment', 'icon': 'fas fa-building', 'order': 1},
            {'name': 'فيلا', 'name_en': 'Villa', 'icon': 'fas fa-home', 'order': 2},
            {'name': 'استوديو', 'name_en': 'Studio', 'icon': 'fas fa-bed', 'order': 3},
            {'name': 'دوبلكس', 'name_en': 'Duplex', 'icon': 'fas fa-building', 'order': 4},
            {'name': 'شاليه', 'name_en': 'Chalet', 'icon': 'fas fa-umbrella-beach', 'order': 5},
        ]
        property_types = {}
        for data in types_data:
            pt, created = PropertyType.objects.get_or_create(name=data['name'], defaults=data)
            property_types[data['name']] = pt
            if created: self.stdout.write(f"  Created property type: {pt.name}")
        superadmin, created = User.objects.get_or_create(
            username='admin',
            defaults={'first_name': 'Super', 'last_name': 'Admin', 'email': 'admin@rentplay.sa',
                      'role': User.Role.SUPERADMIN, 'is_staff': True, 'is_superuser': True, 'is_active': True})
        if created:
            superadmin.set_password('admin123')
            superadmin.save()
            self.stdout.write(self.style.SUCCESS(f"  Created SuperAdmin: admin / admin123"))
        agency, created = Agency.objects.get_or_create(
            slug='rentplay-realty',
            defaults={'name': 'RENTPLAY Realty', 'description': 'وكالة عقارات رائدة', 'phone': '0500000000',
                      'whatsapp': '966500000000', 'email': 'info@rentplay-realty.sa', 'city': 'الرياض',
                      'district': 'العليا', 'status': Agency.Status.ACTIVE})
        if created: self.stdout.write(f"  Created agency: {agency.name}")
        def get_district(city_obj, name):
            return District.objects.filter(city=city_obj, name=name).first()
        riyadh = cities['الرياض']; makkah = cities['مكة المكرمة']; jeddah = cities['جدة']; dammam = cities['الدمام']; madinah = cities['المدينة المنورة']
        properties_data = [
            {'unit_code': 'R001', 'title': 'شقة فاخرة بحي العليا', 'property_type': property_types['شقة'], 'city': riyadh,
             'district': get_district(riyadh, 'العليا'), 'price': 8500, 'rooms': 3, 'bathrooms': 2, 'status': Property.Status.AVAILABLE,
             'phone': '0500000001', 'whatsapp': '966500000001', 'features': 'مكيف، سخان، انترنت، حارس، جراج',
             'description': 'شقة واسعة وفاخرة في قلب الرياض بحي العليا.'},
            {'unit_code': 'R002', 'title': 'فيلا بحي النخيل', 'property_type': property_types['فيلا'], 'city': riyadh,
             'district': get_district(riyadh, 'النخيل'), 'price': 25000, 'rooms': 5, 'bathrooms': 4, 'status': Property.Status.AVAILABLE,
             'phone': '0500000002', 'whatsapp': '966500000002', 'features': 'حديقة، مسبح، مكيف، أمن',
             'description': 'فيلا فاخرة بحديقة خاصة ومسبح.'},
            {'unit_code': 'M001', 'title': 'استوديو بالشوقية', 'property_type': property_types['استوديو'], 'city': makkah,
             'district': get_district(makkah, 'الشوقية'), 'price': 3500, 'rooms': 1, 'bathrooms': 1, 'status': Property.Status.RENTED,
             'phone': '0500000003', 'whatsapp': '966500000003', 'features': 'مكيف، مفروش، قريب من الحرم',
             'description': 'استوديو أنيق بالقرب من الحرم المكي.'},
            {'unit_code': 'J001', 'title': 'شاليه بالبوادي', 'property_type': property_types['شاليه'], 'city': jeddah,
             'district': get_district(jeddah, 'البوادي'), 'price': 12000, 'rooms': 3, 'bathrooms': 2, 'status': Property.Status.AVAILABLE,
             'phone': '0500000004', 'whatsapp': '966500000004', 'features': 'مسبح، شاطئ خاص، مكيف',
             'description': 'شاليه صيفي رائع بإطلالة بحرية.'},
            {'unit_code': 'D001', 'title': 'دوبلكس بالروضة', 'property_type': property_types['دوبلكس'], 'city': dammam,
             'district': get_district(dammam, 'الروضة'), 'price': 7000, 'rooms': 4, 'bathrooms': 2, 'status': Property.Status.AVAILABLE,
             'phone': '0500000005', 'whatsapp': '966500000005', 'features': 'رووف، مكيف، سخان، نت',
             'description': 'دوبلكس عصري بالدمام مع رووف مميز.'},
            {'unit_code': 'MD001', 'title': 'شقة بالعوالي', 'property_type': property_types['شقة'], 'city': madinah,
             'district': get_district(madinah, 'العوالي'), 'price': 4500, 'rooms': 2, 'bathrooms': 1, 'status': Property.Status.RENTED,
             'phone': '0500000006', 'whatsapp': '966500000006', 'features': 'مكيف، مفروش، قريب من المسجد النبوي',
             'description': 'شقة مريحة بالمدينة المنورة.'},
            {'unit_code': 'M002', 'title': 'فيلا بالزاهر', 'property_type': property_types['فيلا'], 'city': makkah,
             'district': get_district(makkah, 'الزاهر'), 'price': 18000, 'rooms': 4, 'bathrooms': 3, 'status': Property.Status.AVAILABLE,
             'phone': '0500000007', 'whatsapp': '966500000007', 'features': 'مسبح خاص، حديقة، أمن',
             'description': 'فيلا فاخرة بمكة المكرمة.'},
            {'unit_code': 'R003', 'title': 'شقة بالسويدي', 'property_type': property_types['شقة'], 'city': riyadh,
             'district': get_district(riyadh, 'السويدي'), 'price': 2500, 'rooms': 1, 'bathrooms': 1, 'status': Property.Status.AVAILABLE,
             'phone': '0500000008', 'whatsapp': '966500000008', 'features': 'مفروش، مكيف، نت',
             'description': 'شقة اقتصادية بالرياض.'},
        ]
        for data in properties_data:
            prop, created = Property.objects.get_or_create(
                unit_code=data['unit_code'],
                defaults={**data, 'agency': agency, 'created_by': superadmin, 'is_published': True})
            if created: self.stdout.write(f"  Created property: {prop.title}")
        from datetime import date, timedelta
        props_for_booking = Property.objects.filter(status=Property.Status.AVAILABLE)[:3]
        for i, prop in enumerate(props_for_booking):
            booking, created = Booking.objects.get_or_create(
                property_unit=prop,
                client_name=f'عميل تجريبي {i+1}',
                defaults={'agency': agency, 'phone': f'050000000{i+1}', 'email': f'client{i+1}@example.com',
                          'start_date': date.today() + timedelta(days=10), 'end_date': date.today() + timedelta(days=190),
                          'duration_months': 6, 'status': Booking.Status.PENDING})
            if created: self.stdout.write(f"  Created booking: {booking.client_name}")
        self.stdout.write(self.style.SUCCESS(_('Demo data created successfully!')))
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO(_('Login credentials:')))
        self.stdout.write(f"  Username: admin")
        self.stdout.write(f"  Password: admin123")
        self.stdout.write(f"  Role: SuperAdmin")

# v8.0: Sale support, Customer DB, Unit Requests

from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rentplay', '0013_building_number_postal_code'),
    ]

    operations = [
        # Property: new sale and media URL fields
        migrations.AddField(
            model_name='property',
            name='listing_type',
            field=models.CharField(
                choices=[('rent', 'للإيجار'), ('sale', 'للبيع'), ('both', 'للبيع والإيجار')],
                default='rent',
                max_length=20,
                verbose_name='نوع العرض',
            ),
        ),
        migrations.AddField(
            model_name='property',
            name='price_sale',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='اتركه فارغاً لو الوحدة ليست للبيع',
                max_digits=12,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name='سعر البيع (ريال)',
            ),
        ),
        migrations.AddField(
            model_name='property',
            name='cover_image_url',
            field=models.URLField(
                blank=True,
                help_text='ضع رابط مباشر للصورة بدلاً من الرفع',
                verbose_name='أو رابط صورة الغلاف',
            ),
        ),
        migrations.AddField(
            model_name='property',
            name='video_url',
            field=models.URLField(
                blank=True,
                help_text='ضع رابط مباشر للفيديو (MP4) أو رابط يوتيوب',
                verbose_name='أو رابط فيديو',
            ),
        ),
        # Customer model
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='الاسم')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='الجوال')),
                ('email', models.EmailField(blank=True, verbose_name='البريد الإلكتروني')),
                ('source', models.CharField(
                    choices=[('booking', 'حجز'), ('unit_request', 'طلب وحدة'), ('manual', 'إضافة يدوية')],
                    default='manual',
                    max_length=20,
                    verbose_name='المصدر',
                )),
                ('notes', models.TextField(blank=True, help_text='ملاحظات داخلية عن العميل', verbose_name='ملاحظات')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإضافة')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')),
                ('agency', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='customers',
                    to='rentplay.agency',
                    verbose_name='الوكالة',
                )),
            ],
            options={
                'verbose_name': 'عميل',
                'verbose_name_plural': 'قاعدة بيانات العملاء',
                'ordering': ['-created_at'],
            },
        ),
        # UnitRequest model
        migrations.CreateModel(
            name='UnitRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='الاسم')),
                ('phone', models.CharField(max_length=20, verbose_name='الجوال')),
                ('email', models.EmailField(blank=True, verbose_name='البريد الإلكتروني')),
                ('city_name', models.CharField(blank=True, max_length=100, verbose_name='المدينة المطلوبة')),
                ('district_name', models.CharField(blank=True, max_length=100, verbose_name='الحي المطلوب')),
                ('rooms', models.PositiveIntegerField(blank=True, null=True, verbose_name='عدد الغرف')),
                ('budget', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='الميزانية (ريال)')),
                ('notes', models.TextField(blank=True, verbose_name='ملاحظات إضافية')),
                ('status', models.CharField(
                    choices=[('new', 'جديد'), ('in_progress', 'قيد المتابعة'), ('closed', 'مغلق')],
                    default='new',
                    max_length=20,
                    verbose_name='الحالة',
                )),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإرسال')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')),
            ],
            options={
                'verbose_name': 'طلب وحدة',
                'verbose_name_plural': 'طلبات الوحدات',
                'ordering': ['-created_at'],
            },
        ),
    ]

# Generated manually for RENTPLAY v7.4

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('rentplay', '0010_agency_fields'),
    ]

    operations = [
        # Add new Property fields
        migrations.AddField(
            model_name='property',
            name='is_price_negotiable',
            field=models.BooleanField(default=False, help_text='ضع علامة ✓ لو الأسعار مرنة وقابلة للفصال', verbose_name='الأسعار قابلة للتفاوض'),
        ),
        migrations.AddField(
            model_name='property',
            name='nearby_services',
            field=models.TextField(blank=True, help_text='اكتب الخدمات القريبة مثل: قريبة من مترو العليا، مدرسة النهضة 500م', verbose_name='خدمات ومرافق قريبة'),
        ),

        # Create HouseRule model
        migrations.CreateModel(
            name='HouseRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='اسم القاعدة')),
                ('icon', models.CharField(blank=True, help_text='مثال: fa-smoking-ban', max_length=50, verbose_name='أيقونة Font Awesome')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='ترتيب العرض')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
            ],
            options={
                'verbose_name': 'قاعدة منزلية',
                'verbose_name_plural': 'قواعد المنزل',
                'ordering': ['order', 'name'],
            },
        ),

        # Create PropertyReport model
        migrations.CreateModel(
            name='PropertyReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reporter_name', models.CharField(max_length=200, verbose_name='اسم المُبلّغ')),
                ('reporter_phone', models.CharField(max_length=20, verbose_name='جوال المُبلّغ')),
                ('reporter_email', models.EmailField(blank=True, max_length=254, verbose_name='إيميل المُبلّغ')),
                ('message', models.TextField(verbose_name='نص البلاغ')),
                ('status', models.CharField(choices=[('new', 'جديد'), ('reviewed', 'تمت المراجعة'), ('resolved', 'تم الحل')], default='new', max_length=20, verbose_name='الحالة')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإرسال')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='rentplay.property', verbose_name='property')),
            ],
            options={
                'verbose_name': 'بلاغ عن وحدة',
                'verbose_name_plural': 'البلاغات',
                'ordering': ['-created_at'],
            },
        ),

        # Create AboutPage model
        migrations.CreateModel(
            name='AboutPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('about_title', models.CharField(default='عن رينت بلاي', max_length=200, verbose_name='عنوان نبذة المنصة')),
                ('about_content', models.TextField(blank=True, help_text='اكتب هنا نبذة عن المنصة وإزاي بتساعد الناس', verbose_name='محتوى نبذة المنصة')),
                ('support_email', models.EmailField(blank=True, max_length=254, verbose_name='إيميل الدعم الفني')),
                ('support_phone', models.CharField(blank=True, max_length=20, verbose_name='جوال الدعم الفني')),
                ('support_whatsapp', models.CharField(blank=True, max_length=15, verbose_name='واتساب الدعم الفني')),
                ('show_contact_form', models.BooleanField(default=True, verbose_name='إظهار نموذج التواصل')),
            ],
            options={
                'verbose_name': 'صفحة من نحن',
                'verbose_name_plural': 'صفحة من نحن',
            },
        ),

        # Add M2M field for house_rules on Property
        migrations.AddField(
            model_name='property',
            name='house_rules',
            field=models.ManyToManyField(blank=True, related_name='properties', to='rentplay.houserule', verbose_name='قواعد المنزل'),
        ),
    ]

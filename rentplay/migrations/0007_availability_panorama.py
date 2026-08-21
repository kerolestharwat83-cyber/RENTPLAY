# Generated manually for RENTPLAY v7.0

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('rentplay', '0006_price_daily_weekly'),
    ]

    operations = [
        migrations.CreateModel(
            name='PropertyAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='date')),
                ('status', models.CharField(choices=[('available', 'Available'), ('booked', 'Booked'), ('blocked', 'Blocked by Owner')], default='available', max_length=20, verbose_name='status')),
                ('notes', models.CharField(blank=True, max_length=200, verbose_name='notes')),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availability_dates', to='rentplay.property', verbose_name='property')),
            ],
            options={
                'verbose_name': 'availability date',
                'verbose_name_plural': 'availability dates',
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='PropertyPanorama',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=100, verbose_name='title')),
                ('image', models.ImageField(upload_to='panoramas/%Y/%m/', verbose_name='panorama image')),
                ('is_primary', models.BooleanField(default=False, verbose_name='primary panorama')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='panoramas', to='rentplay.property', verbose_name='property')),
            ],
            options={
                'verbose_name': '360° panorama',
                'verbose_name_plural': '360° panoramas',
                'ordering': ['-is_primary', '-created_at'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='propertyavailability',
            unique_together={('property', 'date')},
        ),
    ]

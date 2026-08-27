# Generated manually for RENTPLAY v7.5

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentplay', '0012_alter_booking_options_alter_property_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='building_number',
            field=models.CharField(blank=True, help_text='رقم المبنى من العنوان الوطني (اختياري)', max_length=20, verbose_name='رقم المبنى'),
        ),
        migrations.AddField(
            model_name='property',
            name='postal_code',
            field=models.CharField(blank=True, help_text='الرمز البريدي (اختياري)', max_length=10, verbose_name='الرمز البريدي'),
        ),
    ]

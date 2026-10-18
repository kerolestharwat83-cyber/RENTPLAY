# Generated manually for RENTPLAY v6.2

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rentplay', '0004_property_cover_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='street_name',
            field=models.CharField(
                blank=True,
                help_text='اكتب اسم الشارع يدوياً',
                max_length=100,
                verbose_name='اسم الشارع',
            ),
        ),
    ]

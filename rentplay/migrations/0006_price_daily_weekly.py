# Generated manually for RENTPLAY v6.4

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rentplay', '0005_property_street_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='price_daily',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='اتركه فارغاً لو غير متاح',
                max_digits=12,
                null=True,
                verbose_name='السعر اليومي (ريال)',
            ),
        ),
        migrations.AddField(
            model_name='property',
            name='price_weekly',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='اتركه فارغاً لو غير متاح',
                max_digits=12,
                null=True,
                verbose_name='السعر الأسبوعي (ريال)',
            ),
        ),
        migrations.AlterField(
            model_name='property',
            name='price_annual',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='اتركه فارغاً لو غير متاح',
                max_digits=12,
                null=True,
                verbose_name='السعر السنوي (ريال)',
            ),
        ),
    ]

# Generated manually for RENTPLAY v5.0

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rentplay', '0002_banner'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='price_annual',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='السعر السنوي (ريال)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='property',
            name='is_furnished',
            field=models.BooleanField(default=False, verbose_name='مؤثثة/مفروشة'),
        ),
    ]

# Generated manually for RENTPLAY v6.1

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rentplay', '0003_price_annual_is_furnished'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='cover_image',
            field=models.ImageField(
                blank=True,
                help_text='الصورة اللي هتظهر في الصفحة الرئيسية',
                null=True,
                upload_to='properties/covers/%Y/%m/',
                verbose_name='صورة الغلاف',
            ),
        ),
    ]

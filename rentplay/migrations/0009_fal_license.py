# Generated manually for RENTPLAY v7.3

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rentplay', '0008_waitlist_guest'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='fal_license',
            field=models.FileField(blank=True, help_text='صورة أو ملف PDF (اختياري)', null=True, upload_to='licenses/%Y/%m/', verbose_name='رخصة فال العقارية'),
        ),
    ]

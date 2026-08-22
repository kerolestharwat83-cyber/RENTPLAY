# Generated manually for RENTPLAY v7.4

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('rentplay', '0009_fal_license'),
    ]

    operations = [
        # Add new Agency fields
        migrations.AddField(
            model_name='agency',
            name='about',
            field=models.TextField(blank=True, help_text='نبذة تعريفية عن الوكالة/المكتب', verbose_name='لمحة عن الوكالة'),
        ),
        migrations.AddField(
            model_name='agency',
            name='cr_file',
            field=models.FileField(blank=True, help_text='صورة أو PDF للسجل التجاري', null=True, upload_to='agencies/cr/%Y/%m/', verbose_name='ملف السجل التجاري'),
        ),
        migrations.AddField(
            model_name='agency',
            name='cr_number',
            field=models.CharField(blank=True, help_text='رقم السجل التجاري', max_length=50, verbose_name='رقم السجل التجاري'),
        ),
        migrations.AddField(
            model_name='agency',
            name='facebook',
            field=models.URLField(blank=True, verbose_name='فيسبوك'),
        ),
        migrations.AddField(
            model_name='agency',
            name='instagram',
            field=models.URLField(blank=True, verbose_name='انستجرام'),
        ),
        migrations.AddField(
            model_name='agency',
            name='office_address',
            field=models.CharField(blank=True, help_text='عنوان المكتب/الوكالة', max_length=300, verbose_name='عنوان المكتب'),
        ),
        migrations.AddField(
            model_name='agency',
            name='tiktok',
            field=models.URLField(blank=True, verbose_name='تيك توك'),
        ),
        migrations.AddField(
            model_name='agency',
            name='website',
            field=models.URLField(blank=True, help_text='رابط موقع الوكالة الإلكتروني', verbose_name='موقع الوكالة'),
        ),
    ]
